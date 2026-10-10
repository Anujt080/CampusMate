"""CampusMate AI - Deterministic Campus Route & Navigation Engine
---------------------------------------------------------------
Requirements:
- Pure local Python execution (Dijkstra's Shortest Path Algorithm)
- Zero external Map SDKs, Zero API Keys, Zero database
- Zero Gemma model calls for route calculation (instant & quota-free)
- Natural language origin/destination resolution
- Distance calculation in meters & time estimation based on walking speed
- Step-by-step landmark walking instructions
- Clear labeling of DEMO / UNVERIFIED routes vs official survey routes
- Clean, responsive SVG route schematic generation
"""

import json
import re
import heapq
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

MAP_DATA_PATH = Path(__file__).resolve().parent / "campus_map.json"

class CampusMapEngine:
    """Deterministic routing and navigation engine for campus maps."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or MAP_DATA_PATH
        self.metadata: Dict[str, Any] = {}
        self.locations: Dict[str, Dict[str, Any]] = {}
        self.adjacency: Dict[str, List[Tuple[str, int, Dict[str, Any]]]] = {}
        self.load_map()

    def load_map(self):
        """Load and index campus locations and walking edges from JSON."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Campus map dataset not found at {self.data_path}")

        with open(self.data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self.locations = {}
        for loc in data.get("locations", []):
            self.locations[loc["id"]] = loc
            self.adjacency[loc["id"]] = []

        for edge in data.get("edges", []):
            u, v, dist = edge["from"], edge["to"], edge["distance_m"]
            if u in self.locations and v in self.locations:
                # Add bidirectional walking connection
                self.adjacency[u].append((v, dist, edge))
                self.adjacency[v].append((u, dist, edge))

    def get_locations_list(self) -> List[Tuple[str, str]]:
        """Return list of (Display Name, ID) for UI dropdowns."""
        return [(loc["name"], loc["id"]) for loc in sorted(self.locations.values(), key=lambda x: x["name"])]

    def resolve_location(self, query: str) -> Optional[Dict[str, Any]]:
        """Resolve a free-form name or snippet to a known campus location."""
        if not query:
            return None
        clean = query.strip().lower()

        # 1. Direct ID match
        if clean in self.locations:
            return self.locations[clean]

        # 2. Exact name match
        for loc in self.locations.values():
            if loc["name"].lower() == clean:
                return loc

        # 3. Exact alias match
        for loc in self.locations.values():
            for alias in loc.get("aliases", []):
                if alias.lower() == clean:
                    return loc

        # 4. Substring / Token containment match (ordered by specificity)
        best_match = None
        best_len = 0
        for loc in self.locations.values():
            for alias in loc.get("aliases", []) + [loc["name"].lower()]:
                if alias in clean or clean in alias:
                    if len(alias) > best_len:
                        best_len = len(alias)
                        best_match = loc

        return best_match

    def parse_natural_language_query(self, query: str) -> Tuple[Optional[str], Optional[str], str]:
        """
        Extract starting point and destination from student natural language requests.
        Examples:
        - "I'm standing in front of the canteen. Take me to the CSE block."
        - "From library to main gate"
        - "How to reach mechanical workshop from sports complex"
        """
        q_lower = query.lower()

        start_loc = None
        end_loc = None

        # Pattern 1: "from <start> to <end>"
        m1 = re.search(r"from\s+([^,.\n]+?)\s+to\s+([^,.\n]+)", q_lower)
        if m1:
            start_cand = self.resolve_location(m1.group(1))
            end_cand = self.resolve_location(m1.group(2))
            if start_cand and end_cand:
                return start_cand["id"], end_cand["id"], "Detected from natural language phrase ('from X to Y')"

        # Pattern 2: "reach / go to / take me to <end> from <start>"
        m2_rev = re.search(r"(?:reach|go to|take me to|navigate to|to)\s+(?:the\s+)?([^,.\n]+?)\s+from\s+(?:the\s+)?([^,.\n?]+)", q_lower)
        if m2_rev:
            end_cand = self.resolve_location(m2_rev.group(1))
            start_cand = self.resolve_location(m2_rev.group(2))
            if start_cand and end_cand:
                return start_cand["id"], end_cand["id"], "Detected from natural language phrase ('to X from Y')"

        # Pattern 3: "at/near/in front of <start> ... take me to / reach / go to <end>"
        m2 = re.search(r"(?:at|near|standing in front of|outside)\s+([^,.\n]+?)(?:[.,;]|\s+take|\s+how|\s+go|\s+guide|\s+navigate)", q_lower)
        m2_dest = re.search(r"(?:to|reach|find|take me to|headed to)\s+(?:the\s+)?([^,.\n?]+)", q_lower)
        if m2 and m2_dest:
            start_cand = self.resolve_location(m2.group(1))
            end_cand = self.resolve_location(m2_dest.group(1))
            if start_cand and end_cand and start_cand["id"] != end_cand["id"]:
                return start_cand["id"], end_cand["id"], "Extracted landmark context"

        # Pattern 3: Scan all known aliases and check their position in the sentence
        matched_locs = []
        for loc in self.locations.values():
            for alias in loc.get("aliases", []):
                idx = q_lower.find(alias)
                if idx != -1:
                    matched_locs.append((idx, len(alias), loc["id"]))
                    break

        if len(matched_locs) >= 2:
            # Sort by occurrence in sentence
            matched_locs.sort(key=lambda x: x[0])
            start_id = matched_locs[0][2]
            # Choose distinct destination with largest token match
            for candidate in matched_locs[1:]:
                if candidate[2] != start_id:
                    return start_id, candidate[2], "Matched campus landmarks in query order"

        return None, None, "Could not unambiguously detect both start and destination"

    def find_shortest_route(self, start_id: str, end_id: str, walking_speed_mps: float = 1.2) -> Dict[str, Any]:
        """
        Dijkstra's algorithm: find the shortest walking route between two nodes.
        Returns distance, time, ordered steps, and landmark descriptions.
        """
        if start_id not in self.locations:
            return {"status": "error", "message": f"Unknown origin location ID: '{start_id}'"}
        if end_id not in self.locations:
            return {"status": "error", "message": f"Unknown destination location ID: '{end_id}'"}

        start_loc = self.locations[start_id]
        end_loc = self.locations[end_id]

        if start_id == end_id:
            return {
                "status": "success",
                "start": start_loc,
                "end": end_loc,
                "total_distance_m": 0,
                "estimated_time_sec": 0,
                "estimated_time_str": "0 min (You are already at this destination)",
                "steps": [{
                    "step_num": 1,
                    "from_name": start_loc["name"],
                    "to_name": end_loc["name"],
                    "distance_m": 0,
                    "instruction": f"You are already at {start_loc['name']}.",
                    "landmarks": [],
                    "accessible": True,
                    "verified": True
                }],
                "path_ids": [start_id],
                "path_names": [start_loc["name"]],
                "is_verified": False,
                "is_accessible": True,
                "demo_notice": "DEMO ROUTE (Sample Campus Graph)"
            }

        # Dijkstra priority queue: (distance, current_node, path_nodes, path_edges)
        pq = [(0, start_id, [start_id], [])]
        visited = set()
        best_distances = {start_id: 0}

        shortest_path = None
        shortest_edges = None
        min_total_dist = float("inf")

        while pq:
            current_dist, u, path, edges = heapq.heappop(pq)

            if u in visited and current_dist > best_distances.get(u, float("inf")):
                continue
            visited.add(u)

            if u == end_id:
                shortest_path = path
                shortest_edges = edges
                min_total_dist = current_dist
                break

            for v, edge_dist, edge_data in self.adjacency.get(u, []):
                new_dist = current_dist + edge_dist
                if new_dist < best_distances.get(v, float("inf")):
                    best_distances[v] = new_dist
                    heapq.heappush(pq, (new_dist, v, path + [v], edges + [(u, v, edge_data)]))

        if not shortest_path:
            return {
                "status": "unreachable",
                "start": start_loc,
                "end": end_loc,
                "message": f"No walkable path found between {start_loc['name']} and {end_loc['name']} in the local campus dataset."
            }

        # Assemble step-by-step instructions
        steps = []
        is_all_accessible = True
        is_all_verified = True

        for idx, (u, v, edge_data) in enumerate(shortest_edges, start=1):
            u_loc = self.locations[u]
            v_loc = self.locations[v]

            # Choose directional instruction
            if edge_data["from"] == u and edge_data["to"] == v:
                instruction = edge_data.get("instruction_forward", f"Walk toward {v_loc['name']}.")
            else:
                instruction = edge_data.get("instruction_backward", f"Walk toward {v_loc['name']}.")

            accessible = edge_data.get("accessible", True)
            verified = edge_data.get("verified", False)
            if not accessible:
                is_all_accessible = False
            if not verified:
                is_all_verified = False

            steps.append({
                "step_num": idx,
                "from_name": u_loc["name"],
                "to_name": v_loc["name"],
                "distance_m": edge_data["distance_m"],
                "instruction": instruction,
                "landmarks": edge_data.get("landmarks", []),
                "accessible": accessible,
                "verified": verified
            })

        # Calculate walking time
        speed = walking_speed_mps or self.metadata.get("default_walking_speed_mps", 1.2)
        time_sec = int(min_total_dist / speed)
        mins = time_sec // 60
        secs = time_sec % 60
        time_str = f"{mins} min {secs} sec" if mins > 0 else f"{secs} sec"

        return {
            "status": "success",
            "start": start_loc,
            "end": end_loc,
            "total_distance_m": min_total_dist,
            "estimated_time_sec": time_sec,
            "estimated_time_str": time_str,
            "steps": steps,
            "path_ids": shortest_path,
            "path_names": [self.locations[node_id]["name"] for node_id in shortest_path],
            "is_verified": is_all_verified,
            "is_accessible": is_all_accessible,
            "demo_notice": "DEMO ROUTE (Sample Campus Graph • Not Surveyor Verified)"
        }

    def render_route_markdown(self, route_result: Dict[str, Any]) -> str:
        """Render high-contrast, formatted Markdown directions."""
        if route_result.get("status") != "success":
            return f"⚠️ **Navigation Notice:** {route_result.get('message', 'Unable to resolve route.')}"

        start_name = route_result["start"]["name"]
        end_name = route_result["end"]["name"]
        dist_m = route_result["total_distance_m"]
        time_str = route_result["estimated_time_str"]
        accessible_str = "♿ Wheelchair Accessible" if route_result.get("is_accessible") else "⚠️ Includes stairs/unpaved segments"

        md = []
        md.append(f"## 🧭 Campus Walking Route: {start_name} ➔ {end_name}\n")
        md.append(f"> ⏱️ **Est. Walk:** **{time_str}** | 📏 **Distance:** **{dist_m} meters** | {accessible_str}\n")
        md.append("---\n")
        md.append("### 🚶 Step-by-Step Directions\n")

        for step in route_result["steps"]:
            num = step["step_num"]
            step_dist = step["distance_m"]
            inst = step["instruction"]
            lms = step["landmarks"]
            acc_icon = "♿" if step.get("accessible") else "🪜"

            lm_str = f" *(Landmarks: {', '.join(lms)})*" if lms else ""
            md.append(f"{num}. **{inst}**{lm_str}  \n   `{step_dist}m` • {acc_icon} *Toward {step['to_name']}*")

        md.append("\n---\n")
        md.append(
            "### ℹ️ Campus Walking Notes\n"
            "Walking times are calculated at a standard pace of 1.2 m/s based on local pathway data in `campus_map.json`. "
            "Actual walking times may vary depending on conditions."
        )

        return "\n".join(md)

    def render_route_svg(self, route_result: Dict[str, Any], is_dark: bool = False) -> str:
        """
        Generate a clean, high-contrast SVG schematic visualizing the path between landmarks.
        No external dependencies required!
        """
        if route_result.get("status") != "success":
            return ""

        path_nodes = route_result.get("path_ids", [])
        if not path_nodes:
            return ""

        # Layout parameters for linear schematic
        num_nodes = len(path_nodes)
        node_width = 160
        padding = 40
        svg_width = max(680, num_nodes * node_width + padding * 2)
        svg_height = 160

        # Colors based on theme
        bg_card = "#1e293b" if is_dark else "#ffffff"
        border_col = "#334155" if is_dark else "#e2e8f0"
        text_primary = "#f8fafc" if is_dark else "#0f172a"
        text_muted = "#94a3b8" if is_dark else "#64748b"
        line_col = "#3b82f6"
        start_col = "#10b981"  # Emerald
        end_col = "#6366f1"    # Indigo
        mid_col = "#0ea5e9"    # Sky

        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_width} {svg_height}" width="100%" height="{svg_height}" style="background:{bg_card}; border-radius:12px; border:1px solid {border_col}; margin-top:12px;">',
            f'<defs>',
            f'  <marker id="arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">',
            f'    <path d="M 0 1 L 10 5 L 0 9 z" fill="{line_col}"/>',
            f'  </marker>',
            f'</defs>',
            # Header label inside SVG
            f'<text x="24" y="28" font-family="-apple-system, sans-serif" font-size="12" font-weight="700" fill="{text_muted}">CAMPUS WALKING PATH SCHEMATIC</text>',
            f'<text x="{svg_width - 24}" y="28" text-anchor="end" font-family="-apple-system, sans-serif" font-size="11" font-weight="600" fill="{text_muted}">{route_result["total_distance_m"]}m total</text>'
        ]

        step_x = (svg_width - padding * 2) / max(1, num_nodes - 1) if num_nodes > 1 else svg_width / 2
        y_pos = 85

        # Draw connecting lines with distances
        for i in range(num_nodes - 1):
            x1 = padding + i * step_x
            x2 = padding + (i + 1) * step_x
            step_info = route_result["steps"][i] if i < len(route_result["steps"]) else None
            dist_str = f"{step_info['distance_m']}m" if step_info else ""

            svg_parts.append(
                f'<line x1="{x1 + 18}" y1="{y_pos}" x2="{x2 - 18}" y2="{y_pos}" stroke="{line_col}" stroke-width="3" stroke-dasharray="4,2" marker-end="url(#arrow)" />'
            )
            # Distance badge above arrow
            mid_x = (x1 + x2) / 2
            svg_parts.append(
                f'<rect x="{mid_x - 22}" y="{y_pos - 20}" width="44" height="16" rx="4" fill="{bg_card}" stroke="{border_col}" stroke-width="1"/>'
            )
            svg_parts.append(
                f'<text x="{mid_x}" y="{y_pos - 8}" text-anchor="middle" font-family="-apple-system, sans-serif" font-size="10" font-weight="700" fill="{text_primary}">{dist_str}</text>'
            )

        # Draw nodes & labels
        for i, node_id in enumerate(path_nodes):
            cx = padding + i * step_x if num_nodes > 1 else svg_width / 2
            node = self.locations[node_id]

            if i == 0:
                color = start_col
                tag = "START"
            elif i == num_nodes - 1:
                color = end_col
                tag = "GOAL"
            else:
                color = mid_col
                tag = f"STEP {i}"

            # Circle pin
            svg_parts.append(f'<circle cx="{cx}" cy="{y_pos}" r="14" fill="{color}" stroke="{bg_card}" stroke-width="3"/>')
            svg_parts.append(f'<text x="{cx}" y="{y_pos + 4}" text-anchor="middle" font-family="-apple-system, sans-serif" font-size="10" font-weight="800" fill="#ffffff">{i + 1}</text>')

            # Role badge (START / STEP / GOAL)
            svg_parts.append(f'<text x="{cx}" y="{y_pos + 30}" text-anchor="middle" font-family="-apple-system, sans-serif" font-size="9" font-weight="700" fill="{color}">{tag}</text>')

            # Node Name
            short_name = node["name"]
            if len(short_name) > 16:
                short_name = short_name[:14] + "..."
            svg_parts.append(f'<text x="{cx}" y="{y_pos + 45}" text-anchor="middle" font-family="-apple-system, sans-serif" font-size="11" font-weight="600" fill="{text_primary}">{short_name}</text>')

        svg_parts.append('</svg>')
        return "\n".join(svg_parts)


# Global engine singleton
_map_engine_instance = None

def get_campus_map_engine() -> CampusMapEngine:
    global _map_engine_instance
    if _map_engine_instance is None:
        _map_engine_instance = CampusMapEngine()
    return _map_engine_instance
