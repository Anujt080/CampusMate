"""CampusMate AI - Academic Notes Module (My Notes)
------------------------------------------------
Provides a Google Drive-inspired academic notes management dashboard:
- Folder-based organization across core engineering subjects
- Live search, filtering by subject, sorting (name, date, size)
- Grid & List view layouts
- Upload new notes (simulated with localStorage persistence)
- Document rename and deletion with confirmation modal
- Document preview modal with academic summaries, KaTeX math, code snippets
- Theme-consistent design (Dark/Light mode, cursor glow, card spotlights)
- Pure frontend persistence with zero external database dependencies
"""

import json
from typing import List, Dict, Any

# -------------------------------------------------------------------
# Core Subject Folders (8 Specified Academic Subjects)
# -------------------------------------------------------------------
SUBJECT_FOLDERS = [
    {
        "id": "dsa",
        "name": "Data Structures & Algorithms",
        "code": "CS201",
        "icon_color": "#3b82f6",  # Blue
        "description": "Arrays, Trees, Graphs, Dynamic Programming & Complexity Analysis"
    },
    {
        "id": "oop",
        "name": "Object Oriented Programming",
        "code": "CS202",
        "icon_color": "#8b5cf6",  # Purple
        "description": "Encapsulation, Inheritance, Polymorphism, Design Patterns & Interfaces"
    },
    {
        "id": "os",
        "name": "Operating Systems",
        "code": "CS203",
        "icon_color": "#06b6d4",  # Cyan
        "description": "Process Scheduling, Deadlocks, Memory Paging & File Systems"
    },
    {
        "id": "dbms",
        "name": "Database Management Systems",
        "code": "CS204",
        "icon_color": "#10b981",  # Emerald
        "description": "Relational Algebra, SQL, Normalisation (1NF-BCNF) & ACID Transactions"
    },
    {
        "id": "math",
        "name": "Mathematics",
        "code": "MA201",
        "icon_color": "#f59e0b",  # Amber
        "description": "Linear Algebra, Eigenvalues ($Av = \\lambda v$), Calculus & Probability"
    },
    {
        "id": "de",
        "name": "Digital Electronics",
        "code": "EC201",
        "icon_color": "#ec4899",  # Pink
        "description": "Boolean Algebra, K-Maps, Combinational & Sequential Logic Circuits"
    },
    {
        "id": "cn",
        "name": "Computer Networks",
        "code": "CS301",
        "icon_color": "#6366f1",  # Indigo
        "description": "OSI/TCP-IP Layers, Routing (Dijkstra/OSPF), Subnetting & Socket API"
    },
    {
        "id": "se",
        "name": "Software Engineering",
        "code": "CS302",
        "icon_color": "#14b8a6",  # Teal
        "description": "Agile/Scrum, Software Architecture, Testing Paradigms & CI/CD"
    }
]

# -------------------------------------------------------------------
# Realistic Dummy Academic Documents
# -------------------------------------------------------------------
SAMPLE_DOCUMENTS = [
    {
        "id": "doc-dsa-1",
        "name": "Arrays and Strings.pdf",
        "folder": "Data Structures & Algorithms",
        "folder_id": "dsa",
        "file_type": "PDF",
        "size": "2.4 MB",
        "size_bytes": 2516582,
        "last_modified": "16 Nov 2026",
        "timestamp": 1794780000,
        "pages": 38,
        "summary": "Detailed academic notes covering contiguous memory allocation, two-pointer techniques, sliding window subarrays, string hashing algorithms, and prefix sums.",
        "key_topics": [
            "Contiguous memory addressing: Locality of reference and CPU cache lines",
            "Two-Pointer Technique: In-place array partitions with $O(N)$ time complexity",
            "Sliding Window Paradigm: Fixed vs variable size windows for substring optimization",
            "Rabin-Karp Rolling Hash: Polynomial rolling hash algorithm with modulo arithmetic"
        ],
        "equations": [
            "Element Address: $\\text{Address}(A[i]) = \\text{Base} + i \\times \\text{sizeof}(\\text{type})$",
            "Prefix Sum: $P[i] = P[i-1] + A[i]$, where $\\text{RangeSum}(l, r) = P[r] - P[l-1]$",
            "Rolling Hash: $H(s) = \\left( \\sum_{i=0}^{k-1} s[i] \\cdot p^i \\right) \\pmod m$"
        ],
        "sample_code": "def max_subarray_sum(nums):\n    max_sum = curr_sum = nums[0]\n    for x in nums[1:]:\n        curr_sum = max(x, curr_sum + x)\n        max_sum = max(max_sum, curr_sum)\n    return max_sum"
    },
    {
        "id": "doc-dsa-2",
        "name": "Recursion Notes.pdf",
        "folder": "Data Structures & Algorithms",
        "folder_id": "dsa",
        "file_type": "PDF",
        "size": "1.8 MB",
        "size_bytes": 1887436,
        "last_modified": "15 Nov 2026",
        "timestamp": 1794690000,
        "pages": 26,
        "summary": "Call stack allocation during recursive invocations, base condition analysis, recursion tree method, and Master Theorem for divide-and-conquer recurrence relations.",
        "key_topics": [
            "Stack Frame Mechanics: Return address, local variables, and stack overflow guards",
            "Recursion Tree Method: Estimating work per level in divide-and-conquer",
            "Master Theorem: Asymptotic bounds for $T(N) = aT(N/b) + f(N)$",
            "Tail Call Optimization: Compiler transformation of tail recursion into iteration"
        ],
        "equations": [
            "Master Theorem: $T(N) = aT(N/b) + \\Theta(N^d)$",
            "Case 1: If $d < \\log_b a$, then $T(N) = \\Theta(N^{\\log_b a})$",
            "Case 2: If $d = \\log_b a$, then $T(N) = \\Theta(N^d \\log N)$"
        ],
        "sample_code": "def binary_search(arr, low, high, target):\n    if low > high:\n        return -1\n    mid = (low + high) // 2\n    if arr[mid] == target:\n        return mid\n    elif arr[mid] > target:\n        return binary_search(arr, low, mid - 1, target)\n    else:\n        return binary_search(arr, mid + 1, high, target)"
    },
    {
        "id": "doc-dsa-3",
        "name": "Sorting Algorithms.pdf",
        "folder": "Data Structures & Algorithms",
        "folder_id": "dsa",
        "file_type": "PDF",
        "size": "3.1 MB",
        "size_bytes": 3250585,
        "last_modified": "13 Nov 2026",
        "timestamp": 1794520000,
        "pages": 46,
        "summary": "Comprehensive analysis of comparison-based sorts (QuickSort, MergeSort, HeapSort) and linear sorts (Radix Sort, Counting Sort) with stability and space guarantees.",
        "key_topics": [
            "QuickSort Partition Schemes: Lomuto vs Hoare partitioning and pivot selection",
            "MergeSort Invariant: Stable divide-and-conquer with $O(N)$ auxiliary memory",
            "HeapSort: Binary heap heapify operations with $O(N \\log N)$ worst-case guarantee",
            "Comparison Lower Bound: Proof of $\\Omega(N \\log N)$ decision tree height"
        ],
        "equations": [
            "Comparison Sort Lower Bound: $\\log_2(N!) = \\Omega(N \\log N)$",
            "QuickSort Recurrence: $T(N) = 2T(N/2) + \\Theta(N) \\implies O(N \\log N)$ avg"
        ],
        "sample_code": "def quick_sort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    mid = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return quick_sort(left) + mid + quick_sort(right)"
    },
    {
        "id": "doc-oop-1",
        "name": "OOPS Fundamentals.pdf",
        "folder": "Object Oriented Programming",
        "folder_id": "oop",
        "file_type": "PDF",
        "size": "2.0 MB",
        "size_bytes": 2097152,
        "last_modified": "16 Nov 2026",
        "timestamp": 1794770000,
        "pages": 34,
        "summary": "Core pillars of Object-Oriented programming: Encapsulation, Abstraction, Data Hiding, constructor lifecycle, and memory layout of class instances.",
        "key_topics": [
            "Encapsulation: Bundling data and behavior with access specifiers (public, private, protected)",
            "Abstraction: Exposing interface contracts while concealing internal realization",
            "Constructor Semantics: Default, parameterized, copy constructors and initialization lists",
            "Destructors and RAII: Resource Acquisition Is Initialization for memory leak prevention"
        ],
        "equations": [
            "Coupling Metric: $C_e = \\text{Efferent Coupling}, C_a = \\text{Afferent Coupling}$",
            "Instability Factor: $I = \\frac{C_e}{C_e + C_a}$"
        ],
        "sample_code": "class BankAccount:\n    def __init__(self, owner: str, balance: float = 0.0):\n        self._owner = owner\n        self.__balance = balance\n\n    def deposit(self, amount: float) -> bool:\n        if amount > 0:\n            self.__balance += amount\n            return True\n        return False\n\n    def get_balance(self) -> float:\n        return self.__balance"
    },
    {
        "id": "doc-oop-2",
        "name": "Inheritance and Polymorphism.pdf",
        "folder": "Object Oriented Programming",
        "folder_id": "oop",
        "file_type": "PDF",
        "size": "2.7 MB",
        "size_bytes": 2831155,
        "last_modified": "11 Nov 2026",
        "timestamp": 1794350000,
        "pages": 44,
        "summary": "Method overriding, dynamic dispatch via Virtual Method Tables (vtable), abstract classes, pure virtual methods, and the diamond inheritance problem.",
        "key_topics": [
            "Dynamic Dispatch: Late binding using vtable pointers (vptr) resolved at runtime",
            "Diamond Inheritance: Ambiguity resolution with virtual base classes",
            "Liskov Substitution Principle (LSP): Subtypes must be substitutable for base types",
            "Abstract Base Classes: Enforcing contract adherence in derived subclasses"
        ],
        "equations": [
            "Dynamic Binding Overhead: $\\text{Latency} = \\text{vptr lookup} + \\text{indirect branch}$"
        ],
        "sample_code": "class Shape:\n    def area(self) -> float:\n        raise NotImplementedError(\"Subclass must implement area()\")\n\nclass Circle(Shape):\n    def __init__(self, radius: float):\n        self.radius = radius\n    def area(self) -> float:\n        import math\n        return math.pi * (self.radius ** 2)"
    },
    {
        "id": "doc-os-1",
        "name": "Process Scheduling.pdf",
        "folder": "Operating Systems",
        "folder_id": "os",
        "file_type": "PDF",
        "size": "2.2 MB",
        "size_bytes": 2306867,
        "last_modified": "17 Nov 2026",
        "timestamp": 1794860000,
        "pages": 40,
        "summary": "CPU scheduling algorithms: First-Come First-Served (FCFS), Shortest Job First (SJF), Round Robin (RR) with quantum calibration, and Multi-Level Feedback Queues.",
        "key_topics": [
            "Process Control Block (PCB): Context switching overhead, register save/restore",
            "Convoy Effect: FCFS scheduling bottlenecks caused by CPU-bound tasks",
            "Round Robin Time Quantum: Tradeoff between responsiveness and context switch cost",
            "Multi-Level Feedback Queue: Dynamic priority adjustment based on CPU burst history"
        ],
        "equations": [
            "Turnaround Time: $T_{\\text{turnaround}} = T_{\\text{completion}} - T_{\\text{arrival}}$",
            "Waiting Time: $T_{\\text{waiting}} = T_{\\text{turnaround}} - T_{\\text{burst}}$",
            "CPU Utilization: $\\mu = \\frac{\\sum T_{\\text{burst}}}{\\text{Total Elapsed Time}} \\times 100\\%$"
        ],
        "sample_code": "# Round Robin Queue simulation\ndef round_robin_step(queue, quantum):\n    process = queue.pop(0)\n    runtime = min(process['remaining'], quantum)\n    process['remaining'] -= runtime\n    if process['remaining'] > 0:\n        queue.append(process)\n    return process['id'], runtime"
    },
    {
        "id": "doc-os-2",
        "name": "Memory Management.pdf",
        "folder": "Operating Systems",
        "folder_id": "os",
        "file_type": "PDF",
        "size": "3.4 MB",
        "size_bytes": 3565158,
        "last_modified": "14 Nov 2026",
        "timestamp": 1794600000,
        "pages": 58,
        "summary": "Paging architecture, segmentation, Translation Lookaside Buffer (TLB) hit ratios, page replacement algorithms (FIFO, LRU, Optimal), and thrashing mitigation.",
        "key_topics": [
            "Virtual Address Translation: Page directory, page table entry (PTE), and frame offsets",
            "TLB Effectiveness: Effective Memory Access Time (EMAT) calculations",
            "Page Fault Handling: Page-in from swap partition and dirty bit write-backs",
            "Belady's Anomaly: FIFO page faults increasing with added physical page frames"
        ],
        "equations": [
            "EMAT: $\\text{EMAT} = h \\times (t_{\\text{TLB}} + t_{\\text{mem}}) + (1 - h) \\times (t_{\\text{TLB}} + 2 \\cdot t_{\\text{mem}})$",
            "Page Size Equation: $\\text{Logical Address} = p \\cdot 2^d + d$"
        ],
        "sample_code": "# LRU Page Replacement Cache\nfrom collections import OrderedDict\nclass LRUCache:\n    def __init__(self, capacity: int):\n        self.capacity = capacity\n        self.cache = OrderedDict()\n    def get(self, key):\n        if key not in self.cache: return -1\n        self.cache.move_to_end(key)\n        return self.cache[key]"
    },
    {
        "id": "doc-dbms-1",
        "name": "DBMS Normalisation.pdf",
        "folder": "Database Management Systems",
        "folder_id": "dbms",
        "file_type": "PDF",
        "size": "1.9 MB",
        "size_bytes": 1992294,
        "last_modified": "17 Nov 2026",
        "timestamp": 1794870000,
        "pages": 32,
        "summary": "Functional dependencies, closure of attribute sets, 1NF, 2NF, 3NF, Boyce-Codd Normal Form (BCNF), lossless join decomposition, and dependency preservation tests.",
        "key_topics": [
            "Functional Dependency: $X \\to Y$ definition and Armstrong's Axioms",
            "Attribute Closure: Computing $X^+$ under a set of functional dependencies $F$",
            "First Normal Form (1NF): Eliminating repeating groups and multi-valued attributes",
            "BCNF Rule: For every non-trivial $X \\to Y$, $X$ must be a superkey"
        ],
        "equations": [
            "Lossless Join Criterion: $R_1 \\cap R_2 \\to R_1$ OR $R_1 \\cap R_2 \\to R_2$",
            "Armstrong Transitivity: If $X \\to Y$ and $Y \\to Z$, then $X \\to Z$"
        ],
        "sample_code": "-- BCNF Schema Decomposition\nCREATE TABLE Student_Department (\n    student_id INT PRIMARY KEY,\n    dept_id VARCHAR(10) NOT NULL REFERENCES Department(dept_id)\n);\nCREATE TABLE Department (\n    dept_id VARCHAR(10) PRIMARY KEY,\n    dept_name VARCHAR(100) NOT NULL,\n    hod_name VARCHAR(100)\n);"
    },
    {
        "id": "doc-dbms-2",
        "name": "SQL Queries.pdf",
        "folder": "Database Management Systems",
        "folder_id": "dbms",
        "file_type": "PDF",
        "size": "1.5 MB",
        "size_bytes": 1572864,
        "last_modified": "15 Nov 2026",
        "timestamp": 1794700000,
        "pages": 24,
        "summary": "Complex multi-table JOIN operations, subqueries, correlated subqueries, window functions (ROW_NUMBER, RANK, DENSE_RANK), and transaction ACID guarantees.",
        "key_topics": [
            "JOIN Operations: INNER, LEFT OUTER, RIGHT OUTER, FULL OUTER, and CROSS JOIN",
            "Window Functions: OVER (PARTITION BY ... ORDER BY ...) aggregation semantics",
            "Correlated Subqueries: Query evaluation per outer row and EXISTS optimizations",
            "ACID Properties: Atomicity, Consistency, Isolation levels (Read Committed, Serializable)"
        ],
        "equations": [
            "Relational Theta Join: $R \\bowtie_{\\theta} S = \\sigma_{\\theta}(R \\times S)$",
            "Relational Projection: $\\Pi_{A_1, \\dots, A_k}(R)$"
        ],
        "sample_code": "-- Top 3 Students Per Department using Window Function\nSELECT student_id, student_name, dept_id, gpa\nFROM (\n    SELECT student_id, student_name, dept_id, gpa,\n           DENSE_RANK() OVER (PARTITION BY dept_id ORDER BY gpa DESC) as rank_pos\n    FROM Students\n) ranked\nWHERE rank_pos <= 3;"
    },
    {
        "id": "doc-math-1",
        "name": "Matrices and Determinants.pdf",
        "folder": "Mathematics",
        "folder_id": "math",
        "file_type": "PDF",
        "size": "2.8 MB",
        "size_bytes": 2936012,
        "last_modified": "16 Nov 2026",
        "timestamp": 1794790000,
        "pages": 48,
        "summary": "Matrix operations, rank of a matrix via echelon form, Gaussian elimination, eigenvalues and eigenvectors ($Av = \\lambda v$), characteristic polynomial, and Cayley-Hamilton theorem.",
        "key_topics": [
            "Matrix Inversion: Gauss-Jordan elimination and Adjugate method: $A^{-1} = \\frac{1}{\\det(A)} \\text{adj}(A)$",
            "Eigenvalue Equation: $\\det(A - \\lambda I) = 0$ characteristic polynomial",
            "Diagonalization: $A = PDP^{-1}$ when $n$ linearly independent eigenvectors exist",
            "Cayley-Hamilton Theorem: Every square matrix satisfies its own characteristic equation"
        ],
        "equations": [
            "Eigenvalue Definition: $A v = \\lambda v \\iff (A - \\lambda I) v = 0$",
            "Characteristic Equation: $\\det(A - \\lambda I) = 0$",
            "Trace and Determinant: $\\text{Tr}(A) = \\sum_{i=1}^n \\lambda_i, \\quad \\det(A) = \\prod_{i=1}^n \\lambda_i$"
        ],
        "sample_code": "# Numpy Eigenvalue Computation\nimport numpy as np\nA = np.array([[4.0, 1.0], [2.0, 3.0]])\neigenvalues, eigenvectors = np.linalg.eig(A)\nprint(f\"Eigenvalues: {eigenvalues}\")\nprint(f\"Eigenvectors:\\n{eigenvectors}\")"
    },
    {
        "id": "doc-de-1",
        "name": "Logic Gates and Boolean Algebra.pdf",
        "folder": "Digital Electronics",
        "folder_id": "de",
        "file_type": "PDF",
        "size": "1.7 MB",
        "size_bytes": 1782579,
        "last_modified": "15 Nov 2026",
        "timestamp": 1794710000,
        "pages": 30,
        "summary": "Boolean postulates, De Morgan's theorems, canonical Sum-of-Products (SOP) and Product-of-Sums (POS), and Karnaugh Map (K-Map) simplification with don't-care states.",
        "key_topics": [
            "Universal Gates: NAND and NOR implementations of all primary Boolean functions",
            "De Morgan's Laws: $\\overline{A \\cdot B} = \\bar{A} + \\bar{B}$ and $\\overline{A + B} = \\bar{A} \\cdot \\bar{B}$",
            "Karnaugh Mapping: Gray code grouping of $2^k$ adjacent cells to eliminate variables",
            "Hazard Mitigation: Static-1 and Static-0 hazard detection using consensus terms"
        ],
        "equations": [
            "De Morgan's First Law: $\\overline{x_1 \\cdot x_2 \\cdots x_n} = \\bar{x}_1 + \\bar{x}_2 + \\cdots + \\bar{x}_n$",
            "Consensus Theorem: $AB + \\bar{A}C + BC = AB + \\bar{A}C$"
        ],
        "sample_code": "# Boolean Logic Verification in Python\ndef xor_gate(a: bool, b: bool) -> bool:\n    return (a and not b) or (not a and b)\n\ndef full_adder(a, b, cin):\n    sum_bit = xor_gate(xor_gate(a, b), cin)\n    cout = (a and b) or (cin and xor_gate(a, b))\n    return sum_bit, cout"
    },
    {
        "id": "doc-cn-1",
        "name": "OSI and TCP-IP Models.pdf",
        "folder": "Computer Networks",
        "folder_id": "cn",
        "file_type": "PDF",
        "size": "2.3 MB",
        "size_bytes": 2411724,
        "last_modified": "14 Nov 2026",
        "timestamp": 1794620000,
        "pages": 42,
        "summary": "7-layer OSI reference model vs 4-layer TCP/IP protocol suite, packet encapsulation/decapsulation, sliding window flow control, and TCP 3-way handshake mechanisms.",
        "key_topics": [
            "Layer Abstractions: Application, Transport, Network, Data Link, and Physical layers",
            "TCP 3-Way Handshake: SYN, SYN-ACK, ACK sequence number synchronization",
            "Sliding Window Protocol: Go-Back-N vs Selective Repeat ARQ window bounds",
            "TCP Congestion Control: Slow Start, Congestion Avoidance, Fast Retransmit, and Fast Recovery"
        ],
        "equations": [
            "Bandwidth-Delay Product: $\\text{BDP} = \\text{Bandwidth (bits/sec)} \\times \\text{RTT (sec)}$",
            "Selective Repeat Window: $W_{\\text{sender}} + W_{\\text{receiver}} \\le 2^m$"
        ],
        "sample_code": "# Python TCP Socket Client Example\nimport socket\ndef send_http_get(host, port=80):\n    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:\n        s.connect((host, port))\n        s.sendall(f\"GET / HTTP/1.1\\r\\nHost: {host}\\r\\nConnection: close\\r\\n\\r\\n\".encode())\n        response = s.recv(4096)\n        return response.decode()"
    },
    {
        "id": "doc-se-1",
        "name": "Software Engineering Agile and Scrum.pdf",
        "folder": "Software Engineering",
        "folder_id": "se",
        "file_type": "PDF",
        "size": "1.6 MB",
        "size_bytes": 1677721,
        "last_modified": "16 Nov 2026",
        "timestamp": 1794760000,
        "pages": 30,
        "summary": "Agile manifesto principles, Scrum rituals (Sprint Planning, Daily Standup, Sprint Review, Retrospective), user story estimation, burndown charts, and CI/CD pipelines.",
        "key_topics": [
            "Agile Principles: Individuals and interactions over processes and tools",
            "Scrum Artifacts: Product Backlog, Sprint Backlog, and Increment of Working Software",
            "Story Point Estimation: Planning Poker and Fibonacci sequence calibration",
            "CI/CD Pipeline Architecture: Automated unit testing, linting, and staged deployment"
        ],
        "equations": [
            "Team Velocity: $V_{\\text{sprint}} = \\sum_{\\text{completed}} \\text{Story Points}$",
            "Sprint Capacity: $C = \\text{Days} \\times \\text{Hours/Day} \\times \\text{Focus Factor (e.g., 0.7)}$"
        ],
        "sample_code": "# Agile User Story Data Model\nfrom dataclasses import dataclass\n@dataclass\nclass UserStory:\n    role: str\n    goal: str\n    benefit: str\n    points: int\n    def __str__(self):\n        return f\"As a {self.role}, I want to {self.goal} so that {self.benefit}. (Estimate: {self.points} pts)\""
    }
]

# -------------------------------------------------------------------
# HTML Template Generator for My Notes Webpage
# -------------------------------------------------------------------
def get_notes_page_html() -> str:
    """Returns the comprehensive, interactive HTML structure for My Notes."""
    folders_json = json.dumps(SUBJECT_FOLDERS)
    sample_docs_json = json.dumps(SAMPLE_DOCUMENTS)

    return f"""
<!-- CAMPUSMATE AI - MY NOTES WEBPAGE CONTAINER -->
<div class="notes-page-root">
    <!-- Ambient Background Effects -->
    <div class="ambient-light-bg" aria-hidden="true">
        <div class="ambient-orb-1"></div>
        <div class="ambient-orb-2"></div>
    </div>
    <div id="ambient-cursor-glow" aria-hidden="true"></div>

    <div class="app-container notes-container">
        <!-- 1. Dedicated Top Navigation Bar for My Notes -->
        <header class="campus-navbar notes-navbar" role="banner">
            <div class="nav-left">
                <a href="/" class="nav-brand-logo" title="CampusMate AI Home" aria-label="CampusMate AI Home">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                        <path d="M6 12v5c3 3 9 3 12 0v-5"/>
                    </svg>
                </a>
                <div>
                    <a href="/" class="nav-brand-name" style="text-decoration: none; color: inherit;">CampusMate AI</a>
                </div>
                <div class="nav-model-pill notes-drive-pill">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/>
                        <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/>
                    </svg>
                    <span>Academic Drive</span>
                </div>
            </div>

            <div class="nav-actions">
                <!-- Back to CampusMate AI Button -->
                <a href="/" class="nav-back-btn" title="Back to CampusMate Chatbot" aria-label="Back to CampusMate">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M19 12H5M12 19l-7-7 7-7"/>
                    </svg>
                    <span>Back to CampusMate</span>
                </a>

                <!-- Theme Toggle Button -->
                <button id="theme-toggle-notes" class="theme-toggle-btn" onclick="toggleCampusMateTheme()" title="Switch Light/Dark Mode" aria-label="Toggle theme">
                    <span id="theme-icon-notes">🌙</span> <span id="theme-text-notes">Dark</span>
                </button>
            </div>
        </header>

        <!-- 2. Page Header / Hero Section -->
        <section class="notes-hero-box" aria-labelledby="notes-page-heading">
            <div class="notes-hero-header">
                <div>
                    <h1 id="notes-page-heading" class="notes-title">
                        <span class="notes-title-icon" aria-hidden="true">📖</span> My Notes
                    </h1>
                    <p class="notes-subtitle">Your academic resources, organised in one place.</p>
                </div>
                <div class="notes-hero-stats" id="notes-stats-banner">
                    <div class="stat-item">
                        <span class="stat-value" id="stat-total-notes">13</span>
                        <span class="stat-label">Documents</span>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-item">
                        <span class="stat-value" id="stat-total-folders">8</span>
                        <span class="stat-label">Subjects</span>
                    </div>
                    <div class="stat-divider"></div>
                    <div class="stat-item">
                        <span class="stat-value" id="stat-total-size">31.4 MB</span>
                        <span class="stat-label">Total Size</span>
                    </div>
                </div>
            </div>
        </section>

        <!-- 3. Top Controls Bar: Search, Filters, View Toggle, Upload Button -->
        <section class="notes-control-bar" aria-label="Notes control panel">
            <!-- Search Input with Clear Button -->
            <div class="notes-search-wrapper">
                <svg class="search-icon" width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="11" cy="11" r="8"></circle>
                    <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                </svg>
                <input 
                    type="text" 
                    id="notes-search-input" 
                    class="notes-search-input" 
                    placeholder="Search notes by title, subject, or keywords (e.g. Arrays, DBMS, SQL)..."
                    aria-label="Search notes"
                    autocomplete="off"
                />
                <button id="search-clear-btn" class="search-clear-btn" title="Clear search" style="display: none;" onclick="CampusNotesApp.clearSearch()">
                    ✕
                </button>
            </div>

            <!-- Action Controls Group -->
            <div class="notes-action-controls">
                <!-- Subject Filter Dropdown -->
                <div class="filter-dropdown-wrapper">
                    <select id="notes-subject-filter" class="notes-select" onchange="CampusNotesApp.onSubjectFilterChange(this.value)" aria-label="Filter by subject">
                        <option value="ALL">All Subjects (8)</option>
                        <option value="Data Structures & Algorithms">Data Structures & Algorithms</option>
                        <option value="Object Oriented Programming">Object Oriented Programming</option>
                        <option value="Operating Systems">Operating Systems</option>
                        <option value="Database Management Systems">Database Management Systems</option>
                        <option value="Mathematics">Mathematics</option>
                        <option value="Digital Electronics">Digital Electronics</option>
                        <option value="Computer Networks">Computer Networks</option>
                        <option value="Software Engineering">Software Engineering</option>
                    </select>
                </div>

                <!-- Sort Dropdown -->
                <div class="sort-dropdown-wrapper">
                    <select id="notes-sort-select" class="notes-select" onchange="CampusNotesApp.onSortChange(this.value)" aria-label="Sort notes">
                        <option value="date-desc">Last Modified (Newest)</option>
                        <option value="date-asc">Last Modified (Oldest)</option>
                        <option value="name-asc">Name (A to Z)</option>
                        <option value="name-desc">Name (Z to A)</option>
                        <option value="size-desc">File Size (Largest)</option>
                    </select>
                </div>

                <!-- Grid / List View Toggle Buttons -->
                <div class="view-toggle-group" role="group" aria-label="View toggle">
                    <button id="view-grid-btn" class="view-toggle-btn active" onclick="CampusNotesApp.setViewMode('grid')" title="Grid View" aria-pressed="true">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <rect x="3" y="3" width="7" height="7"></rect>
                            <rect x="14" y="3" width="7" height="7"></rect>
                            <rect x="14" y="14" width="7" height="7"></rect>
                            <rect x="3" y="14" width="7" height="7"></rect>
                        </svg>
                    </button>
                    <button id="view-list-btn" class="view-toggle-btn" onclick="CampusNotesApp.setViewMode('list')" title="List View" aria-pressed="false">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <line x1="8" y1="6" x2="21" y2="6"></line>
                            <line x1="8" y1="12" x2="21" y2="12"></line>
                            <line x1="8" y1="18" x2="21" y2="18"></line>
                            <line x1="3" y1="6" x2="3.01" y2="6"></line>
                            <line x1="3" y1="12" x2="3.01" y2="12"></line>
                            <line x1="3" y1="18" x2="3.01" y2="18"></line>
                        </svg>
                    </button>
                </div>

                <!-- Primary Action: Upload Notes -->
                <button id="upload-note-btn" class="btn-primary-action upload-btn" onclick="CampusNotesApp.openUploadModal()" title="Upload a new note">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="12" y1="5" x2="12" y2="19"></line>
                        <line x1="5" y1="12" x2="19" y2="12"></line>
                    </svg>
                    <span>Upload Notes</span>
                </button>
            </div>
        </section>

        <!-- 4. Breadcrumbs Trail -->
        <nav class="notes-breadcrumbs" aria-label="Folder Navigation">
            <div id="breadcrumbs-container">
                <span class="crumb active" onclick="CampusNotesApp.resetFolderFilter()">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: -2px; margin-right: 4px;">
                        <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                    </svg>
                    All Notes
                </span>
                <span id="breadcrumb-subfolder" style="display: none;">
                    <span class="crumb-separator">/</span>
                    <span id="breadcrumb-folder-name" class="crumb current"></span>
                </span>
            </div>
            <div class="active-filter-badge" id="active-filter-indicator" style="display: none;">
                <span id="active-filter-text"></span>
                <button onclick="CampusNotesApp.clearFilters()" title="Reset filter">✕</button>
            </div>
        </nav>

        <!-- 5. Subject-Wise Folders Section -->
        <section class="notes-section" id="folders-section" aria-labelledby="folders-heading">
            <div class="section-title-row">
                <h2 id="folders-heading" class="section-heading">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                    </svg>
                    Subject Folders
                </h2>
                <span class="section-badge" id="folders-count-badge">8 subjects</span>
            </div>
            <div class="folders-grid" id="folders-container">
                <!-- Rendered dynamically by CampusNotesApp -->
            </div>
        </section>

        <!-- 6. Recently Opened Section -->
        <section class="notes-section" id="recent-section" aria-labelledby="recent-heading">
            <div class="section-title-row">
                <h2 id="recent-heading" class="section-heading">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    Recently Opened
                </h2>
                <span class="section-badge" id="recent-count-badge">Recent documents</span>
            </div>
            <div class="recent-grid" id="recent-container">
                <!-- Rendered dynamically by CampusNotesApp -->
            </div>
        </section>

        <!-- 7. All / Filtered Documents Section -->
        <section class="notes-section" id="documents-section" aria-labelledby="documents-heading">
            <div class="section-title-row">
                <h2 id="documents-heading" class="section-heading">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                        <polyline points="14 2 14 8 20 8"></polyline>
                        <line x1="16" y1="13" x2="8" y2="13"></line>
                        <line x1="16" y1="17" x2="8" y2="17"></line>
                        <polyline points="10 9 9 9 8 9"></polyline>
                    </svg>
                    <span id="documents-view-title">All Documents</span>
                </h2>
                <span class="section-badge" id="documents-count-badge">0 files</span>
            </div>

            <!-- Documents View Container (Grid or List mode) -->
            <div id="documents-container" class="documents-grid-view">
                <!-- Rendered dynamically by CampusNotesApp -->
            </div>

            <!-- Empty State Container -->
            <div id="notes-empty-state" class="notes-empty-box" style="display: none;">
                <div class="placeholder-icon-wrapper">
                    <span class="placeholder-icon">🔍</span>
                </div>
                <div class="placeholder-title" id="empty-state-title">No documents found</div>
                <div class="placeholder-instruction" id="empty-state-message">
                    Try adjusting your search query or subject filter to find what you're looking for.
                </div>
                <button class="btn-secondary-action empty-reset-btn" onclick="CampusNotesApp.clearFilters()">
                    Reset All Filters
                </button>
            </div>
        </section>

        <!-- 8. Footer Bar -->
        <footer class="footer-bar notes-footer" role="contentinfo">
            CampusMate AI • Academic Notes Management Drive • Grounded on College Curriculum • Zero Database Local Persistence
        </footer>
    </div>
</div>

<!-- ===================================================================
     INTERACTIVE MODALS
     =================================================================== -->

<!-- Modal 1: Upload Notes Modal -->
<div id="modal-upload" class="notes-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-upload-title" style="display: none;">
    <div class="modal-card panel-card">
        <div class="modal-header">
            <h3 id="modal-upload-title" class="modal-title">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent-primary);">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                    <polyline points="17 8 12 3 7 8"></polyline>
                    <line x1="12" y1="3" x2="12" y2="15"></line>
                </svg>
                Upload Academic Note
            </h3>
            <button class="modal-close-btn" onclick="CampusNotesApp.closeUploadModal()" title="Close dialog">✕</button>
        </div>

        <form id="upload-form" class="modal-form" onsubmit="CampusNotesApp.handleUploadSubmit(event)">
            <div class="form-group">
                <label for="upload-doc-title">Document Title / File Name <span class="required-star">*</span></label>
                <input 
                    type="text" 
                    id="upload-doc-title" 
                    class="modal-input" 
                    placeholder="e.g., Graph Algorithms and Minimum Spanning Trees.pdf"
                    required
                />
            </div>

            <div class="form-row">
                <div class="form-group flex-1">
                    <label for="upload-doc-subject">Subject Folder <span class="required-star">*</span></label>
                    <select id="upload-doc-subject" class="modal-select" required>
                        <option value="Data Structures & Algorithms">Data Structures & Algorithms</option>
                        <option value="Object Oriented Programming">Object Oriented Programming</option>
                        <option value="Operating Systems">Operating Systems</option>
                        <option value="Database Management Systems">Database Management Systems</option>
                        <option value="Mathematics">Mathematics</option>
                        <option value="Digital Electronics">Digital Electronics</option>
                        <option value="Computer Networks">Computer Networks</option>
                        <option value="Software Engineering">Software Engineering</option>
                    </select>
                </div>

                <div class="form-group flex-1">
                    <label for="upload-doc-type">File Type</label>
                    <select id="upload-doc-type" class="modal-select">
                        <option value="PDF">PDF (.pdf)</option>
                        <option value="DOCX">Word Document (.docx)</option>
                        <option value="TXT">Plain Text (.txt)</option>
                        <option value="MD">Markdown (.md)</option>
                        <option value="PPTX">Presentation (.pptx)</option>
                    </select>
                </div>
            </div>

            <!-- Simulated Drag and Drop File Picker Zone -->
            <div class="form-group">
                <label>Attach File</label>
                <div class="upload-dropzone" id="upload-dropzone" onclick="document.getElementById('file-picker-input').click()">
                    <input type="file" id="file-picker-input" style="display: none;" onchange="CampusNotesApp.handleFileSelection(event)">
                    <div class="dropzone-icon">📁</div>
                    <div class="dropzone-text" id="dropzone-filename">Click or drag a file to attach</div>
                    <div class="dropzone-sub">Supported formats: PDF, DOCX, TXT, MD, PPTX (up to 50 MB)</div>
                </div>
            </div>

            <div class="form-group">
                <label for="upload-doc-summary">Key Summary / Study Highlights (Optional)</label>
                <textarea 
                    id="upload-doc-summary" 
                    class="modal-textarea" 
                    rows="3" 
                    placeholder="Brief overview of formulas, chapters, or syllabus modules covered in this note..."
                ></textarea>
            </div>

            <div class="modal-footer">
                <button type="button" class="btn-secondary-action" onclick="CampusNotesApp.closeUploadModal()">Cancel</button>
                <button type="submit" class="btn-primary-action" style="margin-top: 0;">Add to Notes</button>
            </div>
        </form>
    </div>
</div>

<!-- Modal 2: Document Preview Modal (Full Reader View) -->
<div id="modal-preview" class="notes-modal-backdrop preview-backdrop" role="dialog" aria-modal="true" aria-labelledby="preview-doc-title" style="display: none;">
    <div class="modal-card preview-card panel-card">
        <div class="preview-header">
            <div class="preview-meta-col">
                <div class="preview-type-badge" id="preview-type-badge">PDF</div>
                <div>
                    <h3 id="preview-doc-title" class="preview-title">Document Title</h3>
                    <div class="preview-sub-meta">
                        <span id="preview-subject" class="preview-subject-badge">Subject</span>
                        <span class="preview-dot">•</span>
                        <span id="preview-size">0 MB</span>
                        <span class="preview-dot">•</span>
                        <span id="preview-date">Date</span>
                    </div>
                </div>
            </div>
            <div class="preview-actions-col">
                <button class="btn-secondary-action preview-action-btn" onclick="CampusNotesApp.simulateDownload()" title="Download document">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="7 10 12 15 17 10"></polyline>
                        <line x1="12" y1="15" x2="12" y2="3"></line>
                    </svg>
                    <span>Download</span>
                </button>
                <button class="modal-close-btn" onclick="CampusNotesApp.closePreviewModal()" title="Close preview">✕</button>
            </div>
        </div>

        <div class="preview-body" id="preview-body-content">
            <!-- Dynamically injected preview content -->
        </div>

        <div class="preview-footer">
            <div class="preview-footer-info">
                <span>📖 Academic Preview Reader</span>
                <span>•</span>
                <span id="preview-pages-info">1 of 1 pages</span>
            </div>
            <button class="btn-secondary-action" onclick="CampusNotesApp.closePreviewModal()">Close Reader</button>
        </div>
    </div>
</div>

<!-- Modal 3: Rename Document Modal -->
<div id="modal-rename" class="notes-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-rename-title" style="display: none;">
    <div class="modal-card panel-card" style="max-width: 480px;">
        <div class="modal-header">
            <h3 id="modal-rename-title" class="modal-title">
                <svg width="19" height="19" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: var(--accent-primary);">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                </svg>
                Rename Document
            </h3>
            <button class="modal-close-btn" onclick="CampusNotesApp.closeRenameModal()" title="Close">✕</button>
        </div>

        <form id="rename-form" class="modal-form" onsubmit="CampusNotesApp.handleRenameSubmit(event)">
            <input type="hidden" id="rename-doc-id" />
            <div class="form-group">
                <label for="rename-doc-input">New Document Name</label>
                <input 
                    type="text" 
                    id="rename-doc-input" 
                    class="modal-input" 
                    required 
                    placeholder="e.g., Arrays and Strings v2.pdf"
                />
            </div>
            <div class="modal-footer">
                <button type="button" class="btn-secondary-action" onclick="CampusNotesApp.closeRenameModal()">Cancel</button>
                <button type="submit" class="btn-primary-action" style="margin-top: 0;">Save Name</button>
            </div>
        </form>
    </div>
</div>

<!-- Modal 4: Delete Confirmation Modal -->
<div id="modal-delete" class="notes-modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="modal-delete-title" style="display: none;">
    <div class="modal-card panel-card" style="max-width: 460px;">
        <div class="modal-header">
            <h3 id="modal-delete-title" class="modal-title" style="color: #ef4444;">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="3 6 5 6 21 6"></polyline>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                    <line x1="10" y1="11" x2="10" y2="17"></line>
                    <line x1="14" y1="11" x2="14" y2="17"></line>
                </svg>
                Delete Document?
            </h3>
            <button class="modal-close-btn" onclick="CampusNotesApp.closeDeleteModal()" title="Close">✕</button>
        </div>

        <div class="modal-body" style="margin: 16px 0;">
            <p style="color: var(--text-primary); font-size: 14px; margin-bottom: 8px;">
                Are you sure you want to permanently delete:
            </p>
            <div class="delete-doc-preview-badge" id="delete-doc-name-preview">
                Document Name
            </div>
            <p style="color: var(--text-muted); font-size: 12.5px; margin-top: 10px;">
                ⚠️ This will remove the document from your local academic storage. This action cannot be undone.
            </p>
            <input type="hidden" id="delete-doc-id" />
        </div>

        <div class="modal-footer">
            <button type="button" class="btn-secondary-action" onclick="CampusNotesApp.closeDeleteModal()">Cancel</button>
            <button type="button" class="btn-danger-action" onclick="CampusNotesApp.handleDeleteConfirm()">Delete Document</button>
        </div>
    </div>
</div>

<!-- ===================================================================
     EMBEDDED CLIENT APPLICATION SCRIPT
     =================================================================== -->
<script>
window.CAMPUS_FOLDERS_DATA = {folders_json};
window.CAMPUS_INITIAL_DOCS = {sample_docs_json};

(function() {{
    const STORAGE_KEY = 'campusmate_notes_v1';
    const VIEW_MODE_KEY = 'campusmate_notes_view';
    const RECENT_KEY = 'campusmate_recent_ids_v1';

    // Application state
    let state = {{
        folders: window.CAMPUS_FOLDERS_DATA || [],
        documents: [],
        recentDocIds: [],
        currentFolder: 'ALL',
        searchQuery: '',
        sortBy: 'date-desc',
        viewMode: 'grid'
    }};

    // Icon helper mapping
    function getFileIconSvg(type) {{
        const upper = (type || 'PDF').toUpperCase();
        if (upper === 'PDF') {{
            return `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="9" y1="15" x2="15" y2="15"></line></svg>`;
        }} else if (upper === 'DOCX' || upper === 'DOC') {{
            return `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>`;
        }} else if (upper === 'MD' || upper === 'TXT') {{
            return `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>`;
        }} else {{
            return `<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><circle cx="12" cy="14" r="2"></circle></svg>`;
        }}
    }}

    // App core namespace
    window.CampusNotesApp = {{
        init: function() {{
            try {{
                const savedDocs = localStorage.getItem(STORAGE_KEY);
                if (savedDocs) {{
                    state.documents = JSON.parse(savedDocs);
                }} else {{
                    state.documents = window.CAMPUS_INITIAL_DOCS || [];
                    this.saveToStorage();
                }}
            }} catch(e) {{
                state.documents = window.CAMPUS_INITIAL_DOCS || [];
            }}

            try {{
                const savedView = localStorage.getItem(VIEW_MODE_KEY);
                if (savedView === 'list' || savedView === 'grid') {{
                    state.viewMode = savedView;
                }}
            }} catch(e) {{}}

            try {{
                const savedRecent = localStorage.getItem(RECENT_KEY);
                if (savedRecent) {{
                    state.recentDocIds = JSON.parse(savedRecent);
                }} else {{
                    state.recentDocIds = state.documents.slice(0, 4).map(d => d.id);
                }}
            }} catch(e) {{
                state.recentDocIds = state.documents.slice(0, 4).map(d => d.id);
            }}

            this.bindEvents();
            this.syncThemeButton();
            this.renderAll();
        }},

        saveToStorage: function() {{
            try {{
                localStorage.setItem(STORAGE_KEY, JSON.stringify(state.documents));
            }} catch(e) {{}}
        }},

        saveRecentToStorage: function() {{
            try {{
                localStorage.setItem(RECENT_KEY, JSON.stringify(state.recentDocIds));
            }} catch(e) {{}}
        }},

        syncThemeButton: function() {{
            try {{
                const currentTheme = localStorage.getItem('campusmate_theme') || 'dark';
                const icon = document.getElementById('theme-icon-notes');
                const text = document.getElementById('theme-text-notes');
                if (icon) icon.textContent = currentTheme === 'dark' ? '☀️' : '🌙';
                if (text) text.textContent = currentTheme === 'dark' ? 'Light' : 'Dark';
            }} catch(e) {{}}
        }},

        bindEvents: function() {{
            const searchInput = document.getElementById('notes-search-input');
            if (searchInput) {{
                searchInput.addEventListener('input', (e) => {{
                    state.searchQuery = e.target.value.trim().toLowerCase();
                    const clearBtn = document.getElementById('search-clear-btn');
                    if (clearBtn) clearBtn.style.display = state.searchQuery ? 'block' : 'none';
                    this.renderDocuments();
                }});
            }}

            // Keyboard accessibility (ESC closes modals)
            window.addEventListener('keydown', (e) => {{
                if (e.key === 'Escape') {{
                    this.closeUploadModal();
                    this.closePreviewModal();
                    this.closeRenameModal();
                    this.closeDeleteModal();
                }}
            }});
        }},

        clearSearch: function() {{
            state.searchQuery = '';
            const searchInput = document.getElementById('notes-search-input');
            if (searchInput) searchInput.value = '';
            const clearBtn = document.getElementById('search-clear-btn');
            if (clearBtn) clearBtn.style.display = 'none';
            this.renderDocuments();
        }},

        clearFilters: function() {{
            state.currentFolder = 'ALL';
            state.searchQuery = '';
            const searchInput = document.getElementById('notes-search-input');
            if (searchInput) searchInput.value = '';
            const filterSelect = document.getElementById('notes-subject-filter');
            if (filterSelect) filterSelect.value = 'ALL';
            const clearBtn = document.getElementById('search-clear-btn');
            if (clearBtn) clearBtn.style.display = 'none';
            this.updateBreadcrumbs();
            this.renderFolders();
            this.renderDocuments();
        }},

        onSubjectFilterChange: function(folderName) {{
            state.currentFolder = folderName;
            this.updateBreadcrumbs();
            this.renderFolders();
            this.renderDocuments();
        }},

        onSortChange: function(sortVal) {{
            state.sortBy = sortVal;
            this.renderDocuments();
        }},

        setViewMode: function(mode) {{
            state.viewMode = mode;
            try {{
                localStorage.setItem(VIEW_MODE_KEY, mode);
            }} catch(e) {{}}
            const gridBtn = document.getElementById('view-grid-btn');
            const listBtn = document.getElementById('view-list-btn');
            if (gridBtn && listBtn) {{
                if (mode === 'grid') {{
                    gridBtn.classList.add('active');
                    gridBtn.setAttribute('aria-pressed', 'true');
                    listBtn.classList.remove('active');
                    listBtn.setAttribute('aria-pressed', 'false');
                }} else {{
                    listBtn.classList.add('active');
                    listBtn.setAttribute('aria-pressed', 'true');
                    gridBtn.classList.remove('active');
                    gridBtn.setAttribute('aria-pressed', 'false');
                }}
            }}
            this.renderDocuments();
        }},

        selectFolder: function(folderName) {{
            state.currentFolder = folderName;
            const filterSelect = document.getElementById('notes-subject-filter');
            if (filterSelect) filterSelect.value = folderName;
            this.updateBreadcrumbs();
            this.renderFolders();
            this.renderDocuments();
            // Smooth scroll to documents section
            const docSection = document.getElementById('documents-section');
            if (docSection) docSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
        }},

        resetFolderFilter: function() {{
            this.selectFolder('ALL');
        }},

        updateBreadcrumbs: function() {{
            const subfolder = document.getElementById('breadcrumb-subfolder');
            const folderNameElem = document.getElementById('breadcrumb-folder-name');
            const activeIndicator = document.getElementById('active-filter-indicator');
            const activeText = document.getElementById('active-filter-text');

            if (state.currentFolder !== 'ALL') {{
                if (subfolder && folderNameElem) {{
                    subfolder.style.display = 'inline-flex';
                    folderNameElem.textContent = state.currentFolder;
                }}
                if (activeIndicator && activeText) {{
                    activeIndicator.style.display = 'inline-flex';
                    activeText.textContent = 'Subject: ' + state.currentFolder;
                }}
            }} else {{
                if (subfolder) subfolder.style.display = 'none';
                if (activeIndicator) activeIndicator.style.display = 'none';
            }}
        }},

        renderAll: function() {{
            this.renderStats();
            this.renderFolders();
            this.renderRecent();
            this.renderDocuments();
            this.updateBreadcrumbs();
            this.setViewMode(state.viewMode);
        }},

        renderStats: function() {{
            const totalNotesElem = document.getElementById('stat-total-notes');
            const totalFoldersElem = document.getElementById('stat-total-folders');
            const totalSizeElem = document.getElementById('stat-total-size');

            if (totalNotesElem) totalNotesElem.textContent = state.documents.length;
            if (totalFoldersElem) totalFoldersElem.textContent = state.folders.length;

            if (totalSizeElem) {{
                const totalBytes = state.documents.reduce((acc, d) => acc + (d.size_bytes || 2000000), 0);
                const mb = (totalBytes / (1024 * 1024)).toFixed(1);
                totalSizeElem.textContent = mb + ' MB';
            }}
        }},

        renderFolders: function() {{
            const container = document.getElementById('folders-container');
            if (!container) return;

            const counts = {{}};
            state.documents.forEach(d => {{
                counts[d.folder] = (counts[d.folder] || 0) + 1;
            }});

            let html = '';
            state.folders.forEach(f => {{
                const count = counts[f.name] || 0;
                const isSelected = state.currentFolder === f.name;
                html += `
                <div class="folder-card panel-card ${{isSelected ? 'selected' : ''}}" onclick="CampusNotesApp.selectFolder('${{f.name.replace(/'/g, "\\\\'")}}')" role="button" tabindex="0">
                    <div class="folder-header">
                        <div class="folder-icon-wrapper" style="background: ${{f.icon_color}}22; color: ${{f.icon_color}};">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                            </svg>
                        </div>
                        <span class="folder-badge">${{f.code}}</span>
                    </div>
                    <div class="folder-name">${{f.name}}</div>
                    <div class="folder-meta">
                        <span>${{count}} ${{count === 1 ? 'document' : 'documents'}}</span>
                        <span class="folder-arrow">➔</span>
                    </div>
                </div>
                `;
            }});
            container.innerHTML = html;
        }},

        renderRecent: function() {{
            const container = document.getElementById('recent-container');
            if (!container) return;

            // Map recentDocIds to docs
            let recentDocs = state.recentDocIds
                .map(id => state.documents.find(d => d.id === id))
                .filter(Boolean);

            if (recentDocs.length === 0) {{
                recentDocs = state.documents.slice(0, 4);
            }}

            let html = '';
            recentDocs.slice(0, 4).forEach(doc => {{
                html += `
                <div class="recent-card panel-card" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')" role="button" tabindex="0">
                    <div class="recent-card-top">
                        <div class="recent-icon">${{getFileIconSvg(doc.file_type)}}</div>
                        <span class="recent-type-badge">${{doc.file_type || 'PDF'}}</span>
                    </div>
                    <div class="recent-doc-name" title="${{doc.name}}">${{doc.name}}</div>
                    <div class="recent-doc-subject">${{doc.folder}}</div>
                    <div class="recent-doc-footer">
                        <span>${{doc.size || '2.0 MB'}}</span>
                        <span>•</span>
                        <span>${{doc.last_modified}}</span>
                    </div>
                </div>
                `;
            }});
            container.innerHTML = html;
        }},

        getFilteredDocuments: function() {{
            return state.documents.filter(doc => {{
                // Folder filter
                if (state.currentFolder !== 'ALL' && doc.folder !== state.currentFolder) {{
                    return false;
                }}
                // Search query
                if (state.searchQuery) {{
                    const query = state.searchQuery;
                    const matchName = (doc.name || '').toLowerCase().includes(query);
                    const matchSubject = (doc.folder || '').toLowerCase().includes(query);
                    const matchType = (doc.file_type || '').toLowerCase().includes(query);
                    const matchSummary = (doc.summary || '').toLowerCase().includes(query);
                    if (!matchName && !matchSubject && !matchType && !matchSummary) {{
                        return false;
                    }}
                }}
                return true;
            }}).sort((a, b) => {{
                if (state.sortBy === 'name-asc') return a.name.localeCompare(b.name);
                if (state.sortBy === 'name-desc') return b.name.localeCompare(a.name);
                if (state.sortBy === 'date-asc') return (a.timestamp || 0) - (b.timestamp || 0);
                if (state.sortBy === 'size-desc') return (b.size_bytes || 0) - (a.size_bytes || 0);
                return (b.timestamp || 0) - (a.timestamp || 0); // date-desc default
            }});
        }},

        renderDocuments: function() {{
            const container = document.getElementById('documents-container');
            const emptyState = document.getElementById('notes-empty-state');
            const viewTitle = document.getElementById('documents-view-title');
            const countBadge = document.getElementById('documents-count-badge');
            if (!container) return;

            const filtered = this.getFilteredDocuments();

            if (viewTitle) {{
                viewTitle.textContent = state.currentFolder === 'ALL' ? 'All Documents' : state.currentFolder;
            }}
            if (countBadge) {{
                countBadge.textContent = `${{filtered.length}} ${{filtered.length === 1 ? 'file' : 'files'}}`;
            }}

            if (filtered.length === 0) {{
                container.style.display = 'none';
                if (emptyState) emptyState.style.display = 'flex';
                return;
            }} else {{
                container.style.display = state.viewMode === 'grid' ? 'grid' : 'block';
                if (emptyState) emptyState.style.display = 'none';
            }}

            if (state.viewMode === 'grid') {{
                container.className = 'documents-grid-view';
                let html = '';
                filtered.forEach(doc => {{
                    html += `
                    <div class="note-card panel-card" role="article">
                        <div class="note-card-top" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')">
                            <div class="note-icon-badge">
                                ${{getFileIconSvg(doc.file_type)}}
                            </div>
                            <span class="note-type-pill">${{doc.file_type || 'PDF'}}</span>
                        </div>

                        <div class="note-card-body" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')">
                            <h4 class="note-name" title="${{doc.name}}">${{doc.name}}</h4>
                            <div class="note-subject-tag">${{doc.folder}}</div>
                        </div>

                        <div class="note-card-footer">
                            <div class="note-meta-info">
                                <span>${{doc.size || '2.0 MB'}}</span>
                                <span>•</span>
                                <span>${{doc.last_modified}}</span>
                            </div>
                            <div class="note-actions-btn-group">
                                <button class="card-action-icon-btn" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')" title="Preview document" aria-label="Preview">
                                    👁️
                                </button>
                                <button class="card-action-icon-btn" onclick="CampusNotesApp.openRenameModal('${{doc.id}}', event)" title="Rename document" aria-label="Rename">
                                    ✏️
                                </button>
                                <button class="card-action-icon-btn danger" onclick="CampusNotesApp.openDeleteModal('${{doc.id}}', event)" title="Delete document" aria-label="Delete">
                                    🗑️
                                </button>
                            </div>
                        </div>
                    </div>
                    `;
                }});
                container.innerHTML = html;
            }} else {{
                container.className = 'documents-list-view';
                let html = `
                <div class="notes-table-wrapper">
                    <table class="notes-table">
                        <thead>
                            <tr>
                                <th style="width: 42%;">Document Name</th>
                                <th style="width: 25%;">Subject</th>
                                <th style="width: 10%;">Size</th>
                                <th style="width: 13%;">Last Modified</th>
                                <th style="width: 10%; text-align: right;">Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                `;
                filtered.forEach(doc => {{
                    html += `
                    <tr class="notes-table-row">
                        <td class="td-name" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')">
                            <div class="td-name-cell">
                                <span class="td-icon">${{getFileIconSvg(doc.file_type)}}</span>
                                <span class="td-title" title="${{doc.name}}">${{doc.name}}</span>
                            </div>
                        </td>
                        <td class="td-subject" onclick="CampusNotesApp.selectFolder('${{doc.folder.replace(/'/g, "\\\\'")}}')">
                            <span class="subject-pill">${{doc.folder}}</span>
                        </td>
                        <td class="td-size">${{doc.size || '2.0 MB'}}</td>
                        <td class="td-date">${{doc.last_modified}}</td>
                        <td class="td-actions">
                            <div class="row-actions-group">
                                <button class="card-action-icon-btn" onclick="CampusNotesApp.openPreviewModal('${{doc.id}}')" title="Preview" aria-label="Preview">👁️</button>
                                <button class="card-action-icon-btn" onclick="CampusNotesApp.openRenameModal('${{doc.id}}', event)" title="Rename" aria-label="Rename">✏️</button>
                                <button class="card-action-icon-btn danger" onclick="CampusNotesApp.openDeleteModal('${{doc.id}}', event)" title="Delete" aria-label="Delete">🗑️</button>
                            </div>
                        </td>
                    </tr>
                    `;
                }});
                html += `
                        </tbody>
                    </table>
                </div>
                `;
                container.innerHTML = html;
            }}
        }},

        // Modal: Upload
        openUploadModal: function() {{
            const modal = document.getElementById('modal-upload');
            if (modal) modal.style.display = 'flex';
            const subjectSelect = document.getElementById('upload-doc-subject');
            if (subjectSelect && state.currentFolder !== 'ALL') {{
                subjectSelect.value = state.currentFolder;
            }}
            const titleInput = document.getElementById('upload-doc-title');
            if (titleInput) {{
                titleInput.value = '';
                setTimeout(() => titleInput.focus(), 100);
            }}
            const dropzoneText = document.getElementById('dropzone-filename');
            if (dropzoneText) dropzoneText.textContent = 'Click or drag a file to attach';
        }},

        closeUploadModal: function() {{
            const modal = document.getElementById('modal-upload');
            if (modal) modal.style.display = 'none';
        }},

        handleFileSelection: function(event) {{
            const file = event.target.files && event.target.files[0];
            if (!file) return;
            const titleInput = document.getElementById('upload-doc-title');
            const dropzoneText = document.getElementById('dropzone-filename');
            if (titleInput && !titleInput.value) {{
                titleInput.value = file.name;
            }}
            if (dropzoneText) {{
                dropzoneText.textContent = `Attached: ${{file.name}} (${{(file.size / (1024*1024)).toFixed(2)}} MB)`;
            }}
        }},

        handleUploadSubmit: function(event) {{
            event.preventDefault();
            const titleInput = document.getElementById('upload-doc-title');
            const subjectSelect = document.getElementById('upload-doc-subject');
            const typeSelect = document.getElementById('upload-doc-type');
            const summaryInput = document.getElementById('upload-doc-summary');

            let title = titleInput.value.trim();
            const subject = subjectSelect.value;
            const fileType = typeSelect.value || 'PDF';
            const summary = summaryInput.value.trim() || 'Custom academic notes uploaded by student.';

            // Ensure sensible file extension
            const ext = '.' + fileType.toLowerCase();
            if (!title.toLowerCase().endsWith(ext)) {{
                title += ext;
            }}

            const now = new Date();
            const dateStr = now.toLocaleDateString('en-GB', {{ day: '2-digit', month: 'short', year: 'numeric' }});

            const newDoc = {{
                id: 'doc-' + Date.now(),
                name: title,
                folder: subject,
                file_type: fileType,
                size: '1.4 MB',
                size_bytes: 1468006,
                last_modified: dateStr,
                timestamp: Math.floor(Date.now() / 1000),
                pages: 18,
                summary: summary,
                key_topics: [
                    'Comprehensive study material uploaded by student',
                    'Key lecture annotations and revision highlights',
                    'Practice exercises and core theoretical concepts'
                ],
                equations: [
                    'Syllabus Core: Continuous revision recommended before exam'
                ],
                sample_code: '# Uploaded Study Notes Reference'
            }};

            state.documents.unshift(newDoc);
            state.recentDocIds.unshift(newDoc.id);
            this.saveToStorage();
            this.saveRecentToStorage();
            this.closeUploadModal();
            this.renderAll();

            if (window.showCampusMateToast) {{
                window.showCampusMateToast(`✓ Note '${{newDoc.name}}' uploaded successfully!`);
            }}
        }},

        // Modal: Preview
        openPreviewModal: function(docId) {{
            const doc = state.documents.find(d => d.id === docId);
            if (!doc) return;

            // Track in recent
            state.recentDocIds = [doc.id, ...state.recentDocIds.filter(id => id !== doc.id)].slice(0, 8);
            this.saveRecentToStorage();
            this.renderRecent();

            const modal = document.getElementById('modal-preview');
            const titleElem = document.getElementById('preview-doc-title');
            const typeBadge = document.getElementById('preview-type-badge');
            const subjectBadge = document.getElementById('preview-subject');
            const sizeElem = document.getElementById('preview-size');
            const dateElem = document.getElementById('preview-date');
            const bodyElem = document.getElementById('preview-body-content');

            if (titleElem) titleElem.textContent = doc.name;
            if (typeBadge) typeBadge.textContent = doc.file_type || 'PDF';
            if (subjectBadge) subjectBadge.textContent = doc.folder;
            if (sizeElem) sizeElem.textContent = doc.size || '2.0 MB';
            if (dateElem) dateElem.textContent = 'Modified: ' + doc.last_modified;

            let bodyHtml = `
            <div class="preview-reader-container">
                <div class="preview-overview-card">
                    <h4 class="preview-section-title">📌 Syllabus & Chapter Overview</h4>
                    <p class="preview-summary-text">${{doc.summary || 'Academic notes resource.'}}</p>
                </div>
            `;

            if (doc.key_topics && doc.key_topics.length > 0) {{
                bodyHtml += `
                <div class="preview-overview-card">
                    <h4 class="preview-section-title">🎯 Core Concepts & Exam Focus Areas</h4>
                    <ul class="preview-bullet-list">
                        ${{doc.key_topics.map(t => `<li>${{t}}</li>`).join('')}}
                    </ul>
                </div>
                `;
            }}

            if (doc.equations && doc.equations.length > 0) {{
                bodyHtml += `
                <div class="preview-overview-card">
                    <h4 class="preview-section-title">📐 Key Mathematical Formulas & Theorems</h4>
                    <div class="preview-formulas-box">
                        ${{doc.equations.map(eq => `<div class="preview-formula-item"><code>${{eq}}</code></div>`).join('')}}
                    </div>
                </div>
                `;
            }}

            if (doc.sample_code) {{
                bodyHtml += `
                <div class="preview-overview-card">
                    <h4 class="preview-section-title">💻 Algorithm Implementation & Data Flow</h4>
                    <pre class="preview-code-block"><code>${{doc.sample_code}}</code></pre>
                </div>
                `;
            }}

            bodyHtml += `
                <div class="preview-footer-note">
                    ℹ️ <b>CampusMate Academic Drive:</b> These notes are verified for undergraduate engineering coursework. 
                    Always consult departmental course handbooks for specific semester syllabus boundaries.
                </div>
            </div>
            `;

            if (bodyElem) bodyElem.innerHTML = bodyHtml;
            if (modal) modal.style.display = 'flex';
        }},

        closePreviewModal: function() {{
            const modal = document.getElementById('modal-preview');
            if (modal) modal.style.display = 'none';
        }},

        simulateDownload: function() {{
            const title = document.getElementById('preview-doc-title');
            const docName = title ? title.textContent : 'academic_note.pdf';
            if (window.showCampusMateToast) {{
                window.showCampusMateToast(`📥 Preparing download for '${{docName}}'...`);
            }}
            setTimeout(() => {{
                if (window.showCampusMateToast) {{
                    window.showCampusMateToast(`✓ '${{docName}}' saved to Downloads.`);
                }}
            }}, 1200);
        }},

        // Modal: Rename
        openRenameModal: function(docId, event) {{
            if (event) event.stopPropagation();
            const doc = state.documents.find(d => d.id === docId);
            if (!doc) return;

            const modal = document.getElementById('modal-rename');
            const idInput = document.getElementById('rename-doc-id');
            const nameInput = document.getElementById('rename-doc-input');

            if (idInput) idInput.value = doc.id;
            if (nameInput) {{
                nameInput.value = doc.name;
                setTimeout(() => nameInput.focus(), 100);
            }}
            if (modal) modal.style.display = 'flex';
        }},

        closeRenameModal: function() {{
            const modal = document.getElementById('modal-rename');
            if (modal) modal.style.display = 'none';
        }},

        handleRenameSubmit: function(event) {{
            event.preventDefault();
            const idInput = document.getElementById('rename-doc-id');
            const nameInput = document.getElementById('rename-doc-input');
            const docId = idInput.value;
            const newName = nameInput.value.trim();

            if (!newName) return;

            const doc = state.documents.find(d => d.id === docId);
            if (doc) {{
                const oldName = doc.name;
                doc.name = newName;
                this.saveToStorage();
                this.renderAll();
                this.closeRenameModal();
                if (window.showCampusMateToast) {{
                    window.showCampusMateToast(`✓ Note renamed to '${{newName}}'`);
                }}
            }}
        }},

        // Modal: Delete
        openDeleteModal: function(docId, event) {{
            if (event) event.stopPropagation();
            const doc = state.documents.find(d => d.id === docId);
            if (!doc) return;

            const modal = document.getElementById('modal-delete');
            const idInput = document.getElementById('delete-doc-id');
            const namePreview = document.getElementById('delete-doc-name-preview');

            if (idInput) idInput.value = doc.id;
            if (namePreview) namePreview.textContent = doc.name;
            if (modal) modal.style.display = 'flex';
        }},

        closeDeleteModal: function() {{
            const modal = document.getElementById('modal-delete');
            if (modal) modal.style.display = 'none';
        }},

        handleDeleteConfirm: function() {{
            const idInput = document.getElementById('delete-doc-id');
            const docId = idInput.value;
            const doc = state.documents.find(d => d.id === docId);
            const docName = doc ? doc.name : 'Note';

            state.documents = state.documents.filter(d => d.id !== docId);
            state.recentDocIds = state.recentDocIds.filter(id => id !== docId);
            this.saveToStorage();
            this.saveRecentToStorage();
            this.closeDeleteModal();
            this.renderAll();

            if (window.showCampusMateToast) {{
                window.showCampusMateToast(`🗑️ '${{docName}}' deleted successfully.`);
            }}
        }}
    }};

    // Auto initialize on DOM ready or immediately if already loaded
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', () => window.CampusNotesApp.init());
    }} else {{
        setTimeout(() => window.CampusNotesApp.init(), 50);
    }}
}})();
</script>
"""

# -------------------------------------------------------------------
# Specialized CSS for My Notes Page
# -------------------------------------------------------------------
NOTES_PAGE_CSS = """
/* =================================================================
   CAMPUSMATE AI - MY NOTES DASHBOARD CSS
   ================================================================= */

/* Page container adjustments */
.notes-page-root {
    position: relative;
    min-height: 100vh;
}

.notes-container {
    max-width: 1200px !important;
}

/* Notes specific navbar adjustments */
.notes-navbar {
    margin-bottom: 24px !important;
}

.notes-drive-pill {
    background: rgba(16, 185, 129, 0.12) !important;
    color: #10b981 !important;
    border-color: rgba(16, 185, 129, 0.25) !important;
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 700;
}

/* Navigation button to My Notes in main CampusMate AI navbar */
.nav-notes-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: linear-gradient(135deg, rgba(37, 99, 235, 0.12), rgba(79, 70, 229, 0.14));
    color: var(--accent-primary) !important;
    border: 1px solid var(--accent-soft-border);
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.nav-notes-btn:hover {
    background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
    color: #ffffff !important;
    border-color: rgba(255, 255, 255, 0.2);
    transform: translateY(-1.5px);
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35);
}

.nav-notes-btn:active {
    transform: translateY(0.5px);
}

/* Back to CampusMate button */
.nav-back-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    background: var(--bg-card-subtle);
    color: var(--text-primary) !important;
    border: 1px solid var(--border-card);
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    text-decoration: none !important;
    cursor: pointer;
    transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.nav-back-btn:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-primary);
    color: var(--accent-hover) !important;
    transform: translateY(-1.5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.nav-back-btn:active {
    transform: translateY(0.5px);
}

/* Hero Section */
.notes-hero-box {
    margin-bottom: 24px;
    position: relative;
    z-index: 1;
}

.notes-hero-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
}

.notes-title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: var(--text-primary);
    margin: 0 0 6px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.notes-title-icon {
    font-size: 30px;
}

.notes-subtitle {
    font-size: 14.5px;
    color: var(--text-secondary);
    margin: 0;
}

.notes-hero-stats {
    display: flex;
    align-items: center;
    gap: 18px;
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 10px 18px;
    box-shadow: var(--shadow-sm);
}

.stat-item {
    display: flex;
    flex-direction: column;
    align-items: center;
}

.stat-value {
    font-size: 17px;
    font-weight: 800;
    color: var(--accent-primary);
}

.stat-label {
    font-size: 11px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.stat-divider {
    width: 1px;
    height: 28px;
    background: var(--border-subtle);
}

/* Control Bar (Search, Filters, View Mode, Upload) */
.notes-control-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 14px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    position: relative;
    z-index: 2;
}

.notes-search-wrapper {
    position: relative;
    flex: 1;
    min-width: 280px;
}

.notes-search-wrapper .search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
}

.notes-search-input {
    width: 100%;
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    border-radius: 12px !important;
    padding: 11px 40px 11px 42px !important;
    font-size: 13.5px !important;
    box-shadow: var(--shadow-sm);
    transition: all 0.2s ease !important;
}

.notes-search-input:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.22) !important;
    outline: none !important;
}

.search-clear-btn {
    position: absolute;
    right: 12px;
    top: 50%;
    transform: translateY(-50%);
    background: transparent;
    border: none;
    color: var(--text-muted);
    font-size: 14px;
    cursor: pointer;
    padding: 4px;
    border-radius: 50%;
}

.search-clear-btn:hover {
    color: var(--text-primary);
}

.notes-action-controls {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}

.notes-select {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    padding: 9px 14px !important;
    font-size: 13px !important;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.notes-select:focus {
    border-color: var(--accent-primary) !important;
    outline: none;
}

.view-toggle-group {
    display: flex;
    align-items: center;
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 3px;
}

.view-toggle-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 34px;
    height: 32px;
    border-radius: 7px;
    border: none;
    background: transparent;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.18s ease;
}

.view-toggle-btn:hover {
    color: var(--text-primary);
}

.view-toggle-btn.active {
    background: var(--bg-card);
    color: var(--accent-primary);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.upload-btn {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-top: 0 !important;
    padding: 9.5px 18px !important;
    font-size: 13.5px !important;
    border-radius: 10px !important;
    cursor: pointer;
}

/* Breadcrumbs */
.notes-breadcrumbs {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 22px;
    font-size: 13px;
    color: var(--text-secondary);
    position: relative;
    z-index: 1;
}

.crumb {
    cursor: pointer;
    font-weight: 600;
    color: var(--text-secondary);
    transition: color 0.18s ease;
}

.crumb:hover {
    color: var(--accent-primary);
}

.crumb.current {
    color: var(--text-primary);
    font-weight: 700;
}

.crumb-separator {
    margin: 0 8px;
    color: var(--text-muted);
}

.active-filter-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--accent-soft);
    color: var(--accent-primary);
    border: 1px solid var(--accent-soft-border);
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
}

.active-filter-badge button {
    background: transparent;
    border: none;
    color: inherit;
    cursor: pointer;
    font-weight: bold;
    font-size: 11px;
}

/* Section Headings */
.notes-section {
    margin-bottom: 30px;
    position: relative;
    z-index: 1;
}

.section-title-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 14px;
}

.section-heading {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 17px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.section-badge {
    font-size: 12px;
    color: var(--text-muted);
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-card);
    padding: 3px 10px;
    border-radius: 9999px;
    font-weight: 600;
}

/* Subject Folders Grid */
.folders-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}

.folder-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    cursor: pointer;
    position: relative;
    overflow: hidden;
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.22s ease,
                box-shadow 0.22s ease,
                background 0.22s ease !important;
    box-shadow: var(--shadow-sm);
}

.folder-card:hover {
    transform: translateY(-3px) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-hover) !important;
    background: var(--bg-card-hover) !important;
}

.folder-card.selected {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 2px var(--accent-primary), var(--shadow-md) !important;
    background: var(--bg-card-hover) !important;
}

.folder-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
}

.folder-icon-wrapper {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border-radius: 10px;
}

.folder-badge {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-muted);
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
    padding: 3px 8px;
    border-radius: 6px;
    letter-spacing: 0.3px;
}

.folder-name {
    font-size: 14.5px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 8px;
    line-height: 1.35;
    min-height: 38px;
}

.folder-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
    color: var(--text-muted);
    font-weight: 500;
}

.folder-arrow {
    font-size: 12px;
    color: var(--accent-primary);
    opacity: 0;
    transform: translateX(-4px);
    transition: all 0.2s ease;
}

.folder-card:hover .folder-arrow {
    opacity: 1;
    transform: translateX(0);
}

/* Recently Opened Grid */
.recent-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
}

.recent-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 14px !important;
    padding: 16px !important;
    cursor: pointer;
    box-shadow: var(--shadow-sm);
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.22s ease,
                box-shadow 0.22s ease !important;
}

.recent-card:hover {
    transform: translateY(-3px) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-hover) !important;
}

.recent-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}

.recent-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}

.recent-type-badge {
    font-size: 10.5px;
    font-weight: 700;
    color: #ef4444;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
    padding: 2px 7px;
    border-radius: 5px;
}

.recent-doc-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 4px;
}

.recent-doc-subject {
    font-size: 12px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 10px;
}

.recent-doc-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    color: var(--text-muted);
}

/* Document Grid View */
.documents-grid-view {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}

.note-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 14px !important;
    padding: 18px !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: var(--shadow-sm);
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                border-color 0.22s ease,
                box-shadow 0.22s ease !important;
    min-height: 180px;
}

.note-card:hover {
    transform: translateY(-3px) !important;
    border-color: var(--border-hover) !important;
    box-shadow: var(--shadow-hover) !important;
}

.note-card-top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 12px;
    cursor: pointer;
}

.note-icon-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
}

.note-type-pill {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--accent-primary);
    background: var(--accent-soft);
    border: 1px solid var(--accent-soft-border);
    padding: 3px 8px;
    border-radius: 6px;
}

.note-card-body {
    flex: 1;
    cursor: pointer;
    margin-bottom: 14px;
}

.note-name {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0 0 6px 0;
    line-height: 1.35;
    word-break: break-word;
}

.note-subject-tag {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-muted);
}

.note-card-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 12px;
    border-top: 1px solid var(--border-subtle);
}

.note-meta-info {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    color: var(--text-muted);
}

.note-actions-btn-group {
    display: flex;
    align-items: center;
    gap: 4px;
}

.card-action-icon-btn {
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
    color: var(--text-secondary);
    border-radius: 7px;
    width: 30px;
    height: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.18s ease;
}

.card-action-icon-btn:hover {
    background: var(--bg-card-hover);
    border-color: var(--accent-primary);
    transform: translateY(-1px);
}

.card-action-icon-btn.danger:hover {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.12);
}

/* Document List View Table */
.documents-list-view {
    display: block;
}

.notes-table-wrapper {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: 14px;
    overflow-x: auto;
    box-shadow: var(--shadow-sm);
}

.notes-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13.5px;
}

.notes-table th {
    text-align: left;
    padding: 12px 18px;
    background: var(--bg-card-subtle);
    border-bottom: 1px solid var(--border-card);
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}

.notes-table td {
    padding: 14px 18px;
    border-bottom: 1px solid var(--border-subtle);
    color: var(--text-primary);
    vertical-align: middle;
}

.notes-table-row {
    transition: background-color 0.18s ease;
}

.notes-table-row:hover {
    background-color: var(--bg-card-hover);
}

.notes-table-row:last-child td {
    border-bottom: none;
}

.td-name {
    cursor: pointer;
}

.td-name-cell {
    display: flex;
    align-items: center;
    gap: 12px;
}

.td-title {
    font-weight: 600;
    color: var(--text-primary);
}

.td-subject {
    cursor: pointer;
}

.subject-pill {
    display: inline-block;
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 12px;
    color: var(--text-secondary);
    font-weight: 500;
}

.td-size, .td-date {
    color: var(--text-muted);
    font-size: 12.5px;
}

.row-actions-group {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px;
}

/* Empty State */
.notes-empty-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 60px 20px;
    background: var(--bg-card);
    border: 1px dashed var(--border-card);
    border-radius: 16px;
    margin-top: 10px;
}

.empty-reset-btn {
    margin-top: 16px;
}

/* Modals */
.notes-modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.65);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 99999;
    padding: 16px;
    animation: fadeInEntrance 0.22s ease-out;
}

.modal-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 18px !important;
    width: 100%;
    max-width: 580px;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4) !important;
}

.modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 14px;
    border-bottom: 1px solid var(--border-subtle);
    margin-bottom: 16px;
}

.modal-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 18px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
}

.modal-close-btn {
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-subtle);
    color: var(--text-muted);
    width: 32px;
    height: 32px;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    transition: all 0.18s ease;
}

.modal-close-btn:hover {
    color: var(--text-primary);
    border-color: var(--accent-primary);
}

.modal-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
}

.form-group label {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--text-secondary);
}

.required-star {
    color: #ef4444;
}

.form-row {
    display: flex;
    gap: 14px;
}

.flex-1 {
    flex: 1;
}

.modal-input, .modal-select, .modal-textarea {
    width: 100%;
    background: var(--bg-card-subtle) !important;
    border: 1px solid var(--border-card) !important;
    color: var(--text-primary) !important;
    border-radius: 10px !important;
    padding: 10px 14px !important;
    font-size: 13.5px !important;
    transition: all 0.2s ease !important;
}

.modal-input:focus, .modal-select:focus, .modal-textarea:focus {
    border-color: var(--accent-primary) !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
    outline: none !important;
}

.upload-dropzone {
    border: 2px dashed var(--border-card);
    border-radius: 12px;
    padding: 22px;
    text-align: center;
    background: var(--bg-card-subtle);
    cursor: pointer;
    transition: all 0.2s ease;
}

.upload-dropzone:hover {
    border-color: var(--accent-primary);
    background: var(--bg-card-hover);
}

.dropzone-icon {
    font-size: 28px;
    margin-bottom: 6px;
}

.dropzone-text {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.dropzone-sub {
    font-size: 11.5px;
    color: var(--text-muted);
}

.modal-footer {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 12px;
    padding-top: 14px;
    border-top: 1px solid var(--border-subtle);
}

.btn-danger-action {
    background: #ef4444 !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    font-size: 13.5px !important;
    padding: 8px 18px !important;
    border-radius: 8px !important;
    border: none !important;
    cursor: pointer;
    transition: all 0.2s ease;
}

.btn-danger-action:hover {
    background: #dc2626 !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
}

.delete-doc-preview-badge {
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-card);
    padding: 10px 14px;
    border-radius: 8px;
    font-weight: 600;
    color: var(--text-primary);
    word-break: break-all;
}

/* Document Reader / Preview Modal */
.preview-card {
    max-width: 820px !important;
    max-height: 88vh;
    display: flex;
    flex-direction: column;
}

.preview-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border-subtle);
    gap: 16px;
}

.preview-meta-col {
    display: flex;
    align-items: center;
    gap: 14px;
    min-width: 0;
}

.preview-type-badge {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    background: rgba(239, 68, 68, 0.12);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #ef4444;
    border-radius: 10px;
    font-weight: 800;
    font-size: 12.5px;
    flex-shrink: 0;
}

.preview-title {
    font-size: 18px;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0 0 4px 0;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 460px;
}

.preview-sub-meta {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12px;
    color: var(--text-muted);
}

.preview-subject-badge {
    font-weight: 600;
    color: var(--accent-primary);
}

.preview-dot {
    opacity: 0.6;
}

.preview-actions-col {
    display: flex;
    align-items: center;
    gap: 8px;
}

.preview-action-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 12px !important;
    font-size: 12px !important;
}

.preview-body {
    flex: 1;
    overflow-y: auto;
    padding: 18px 0;
}

.preview-reader-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
}

.preview-overview-card {
    background: var(--bg-card-subtle);
    border: 1px solid var(--border-card);
    border-radius: 12px;
    padding: 16px 18px;
}

.preview-section-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--accent-primary);
    margin: 0 0 8px 0;
}

.preview-summary-text {
    font-size: 13.5px;
    color: var(--text-secondary);
    line-height: 1.55;
    margin: 0;
}

.preview-bullet-list {
    margin: 0;
    padding-left: 20px;
    font-size: 13px;
    color: var(--text-secondary);
    line-height: 1.6;
}

.preview-formulas-box {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.preview-formula-item code {
    display: block;
    background: var(--code-bg);
    color: #38bdf8 !important;
    padding: 8px 12px;
    border-radius: 8px;
    font-size: 13px;
    border: 1px solid rgba(56, 189, 248, 0.2);
}

.preview-code-block {
    background: var(--code-bg) !important;
    border: 1px solid var(--border-card);
    border-radius: 10px;
    padding: 14px;
    margin: 0;
    overflow-x: auto;
}

.preview-code-block code {
    color: var(--code-text) !important;
    font-size: 12.5px;
    line-height: 1.5;
}

.preview-footer-note {
    font-size: 12px;
    color: var(--text-muted);
    background: var(--bg-card-subtle);
    border-left: 3px solid var(--accent-primary);
    padding: 10px 14px;
    border-radius: 6px;
}

.preview-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 14px;
    border-top: 1px solid var(--border-subtle);
}

.preview-footer-info {
    font-size: 12px;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* =================================================================
   RESPONSIVE MEDIA QUERIES (DESKTOP, LAPTOP, TABLET, MOBILE)
   ================================================================= */
@media (max-width: 1024px) {
    .folders-grid {
        grid-template-columns: repeat(3, 1fr);
    }
    .recent-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .documents-grid-view {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 768px) {
    .notes-hero-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .notes-hero-stats {
        width: 100%;
        justify-content: space-around;
    }
    .folders-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    .recent-grid {
        grid-template-columns: 1fr;
    }
    .documents-grid-view {
        grid-template-columns: 1fr;
    }
    .notes-control-bar {
        flex-direction: column;
        align-items: stretch;
    }
    .notes-action-controls {
        flex-direction: column;
        align-items: stretch;
    }
    .upload-btn {
        justify-content: center;
    }
    .form-row {
        flex-direction: column;
        gap: 12px;
    }
    .preview-header {
        flex-direction: column;
        align-items: flex-start;
    }
    .preview-actions-col {
        width: 100%;
        justify-content: space-between;
    }
}

@media (max-width: 480px) {
    .folders-grid {
        grid-template-columns: 1fr;
    }
}
"""

def build_notes_page():
    """Builds the Gradio component hierarchy for the My Notes webpage."""
    import gradio as gr
    return gr.HTML(value=get_notes_page_html(), elem_classes=["notes-page-component"])
