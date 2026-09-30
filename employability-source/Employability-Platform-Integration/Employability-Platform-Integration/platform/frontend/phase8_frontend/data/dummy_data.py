"""
Static placeholder data standing in for the phase1-phase7 pipeline output.
Every screen reads from here instead of hitting real logic. Swapping this
module for real service calls is the whole point of keeping it separate -
none of the screens should need to change when that happens.
"""

STUDENT = {
    "name": "Aarav Deshpande",
    "initials": "AD",
    "track": "Cloud Computing",
    "semester": "Sem 6",
    "email": "aarav.d@college.edu",
    "phone": "+91 98•••210",
    "enrolment_id": "S-1042",
    "degree": "B.E. Computer Engineering",
    "cgpa": 8.24,
    "github": "github.com/aaravd",
    "linkedin": "linkedin.com/in/aaravd",
    "languages": "English, Hindi, Marathi",
    "profile_completion": 74,
}

SCORE = {
    "overall": 74,
    "band": "Band B",
    "verdict": "Near-ready",
    "cohort_average": 61.4,
    "job_ready_threshold": 80,
    "percentile": 68,
    "cohort_size": 412,
    "points_this_week": 4,
    "confidence": 0.86,
}

SCORE_BREAKDOWN = [
    {"label": "Technical skills", "value": 78, "cohort": 65},
    {"label": "Aptitude", "value": 71, "cohort": 68},
    {"label": "Communication", "value": 66, "cohort": 60},
    {"label": "Resume quality", "value": 68, "cohort": 62},
    {"label": "Projects", "value": 64, "cohort": 58},
    {"label": "Certifications", "value": 48, "cohort": 55},
    {"label": "Company readiness", "value": 73, "cohort": 63},
]

SCORE_DRIVERS = [
    {"label": "CGPA 8.24", "impact": 9.1},
    {"label": "Technical MCQ 82%", "impact": 7.2},
    {"label": "Networking depth", "impact": 4.8},
    {"label": "No IaC exposure", "impact": -7.3},
    {"label": "Thin AWS security", "impact": -4.8},
    {"label": "No internship", "impact": -3.0},
]

SCORE_HISTORY = {
    "months": ["Feb", "Mar", "Apr", "May", "Jun", "Jul"],
    "student": [45, 52, 58, 63, 68, 74],
    "cohort": [40, 44, 48, 52, 57, 61],
    "target": 80,
}

SKILLS_OVERVIEW = [
    {"skill": "Networking", "level": "Strong", "score": 4, "max": 5},
    {"skill": "Python", "level": "Strong", "score": 4, "max": 5},
    {"skill": "Linux admin", "level": "Growing", "score": 3, "max": 5},
    {"skill": "AWS core", "level": "Growing", "score": 2, "max": 5},
    {"skill": "Terraform / IaC", "level": "Gap", "score": 1, "max": 5},
]

QUICK_ACTIONS = [
    {"label": "Continue assessment", "hint": "Technical - 12 of 30 done", "icon": "play"},
    {"label": "Update resume", "hint": "Last uploaded 26 Jul", "icon": "reports"},
    {"label": "Continue learning", "hint": "Week 3 - Terraform", "icon": "book"},
    {"label": "Download report", "hint": "Updated today", "icon": "download"},
]

RECENT_ACTIVITY = [
    {"text": "Your score went from 70 to 74", "when": "Today, 4:12 PM", "kind": "success"},
    {"text": "You finished week 2 of your plan", "when": "Yesterday", "kind": "success"},
    {"text": "AWS Cloud Practitioner added", "when": "27 Jul", "kind": "info"},
    {"text": "You uploaded a new resume", "when": "26 Jul", "kind": "neutral"},
]

JOB_MATCHES = [
    {"role": "Cloud Support Associate", "match": 86},
    {"role": "DevOps Trainee", "match": 74},
    {"role": "SOC Analyst L1", "match": 61},
]

ASSESSMENT_SECTIONS = [
    {"name": "Technical MCQ", "status": "Done", "score": "82%"},
    {"name": "Aptitude", "status": "Done", "score": "71%"},
    {"name": "Communication", "status": "In progress", "score": "6/15 answered"},
    {"name": "Domain - Cloud", "status": "Locked", "score": "45 min - not started"},
]

ASSESSMENT_DOMAINS = [
    {"key": "cloud", "name": "Cloud Computing", "icon": "cloud", "desc": "AWS, networking, IaC, and cloud security fundamentals.", "questions": 10, "minutes": 15},
    {"key": "cyber", "name": "Cybersecurity", "icon": "shield", "desc": "Threats, identity and access, incident response basics.", "questions": 10, "minutes": 15},
]

ASSESSMENT_DIFFICULTIES = [
    {"key": "easy", "name": "Easy", "note": "Recommended for you"},
    {"key": "moderate", "name": "Moderate", "note": "Standard evaluation"},
    {"key": "hard", "name": "Hard", "note": "Advanced scenarios"},
]

# Six questions per domain, two per category, each option carrying its own
# explanation - this is what powers the per-answer feedback and the
# strengths/improvement-areas split on the results page. Real content, not
# lorem ipsum, since a fake explanation would be worse than none.
QUESTION_BANK = {
    "cloud": [
        {
            "id": "c1", "category": "Networking",
            "text": "A web app in a private subnet needs to call an external API over HTTPS, but must never accept inbound connections from the internet. What should you add?",
            "options": [
                {"key": "A", "text": "An internet gateway attached directly to the private subnet"},
                {"key": "B", "text": "A NAT gateway in a public subnet, with the private subnet routing outbound traffic through it"},
                {"key": "C", "text": "A public IP address on the app's instance"},
                {"key": "D", "text": "A VPC peering connection to the internet"},
            ],
            "correct": "B",
            "explanations": {
                "A": "An internet gateway allows two-way traffic - it would expose the subnet to inbound connections too, not just outbound.",
                "B": "Correct. A NAT gateway lets resources in a private subnet start outbound connections (like calling an API) without ever being reachable from outside.",
                "C": "A public IP makes the instance directly reachable from the internet, which is exactly what needs to be avoided here.",
                "D": "VPC peering connects two private networks to each other - it has nothing to do with reaching the public internet.",
            },
        },
        {
            "id": "c2", "category": "Networking",
            "text": "Two servers in the same VPC, different subnets, can't reach each other. Security groups look fine on both. What's the next thing to check?",
            "options": [
                {"key": "A", "text": "Whether the subnets' route tables have a route to each other"},
                {"key": "B", "text": "Whether both servers have the same public IP"},
                {"key": "C", "text": "Whether the VPC has an internet gateway"},
                {"key": "D", "text": "Whether the servers are the same instance type"},
            ],
            "correct": "A",
            "explanations": {
                "A": "Correct. Security groups control what's allowed, but the route table decides whether traffic can get there at all - missing routes are a common cause of same-VPC connectivity issues.",
                "B": "Two servers having the same public IP isn't a real scenario, and public IPs aren't involved in internal VPC routing.",
                "C": "An internet gateway is for internet access, not for traffic between two subnets in the same VPC.",
                "D": "Instance type has no effect on network connectivity between two servers.",
            },
        },
        {
            "id": "c3", "category": "IAM & security",
            "text": "An app on EC2 needs to read from one S3 bucket, with no long-lived credentials stored on the instance. What's the correct approach?",
            "options": [
                {"key": "A", "text": "Store an access key and secret in an environment variable on the instance"},
                {"key": "B", "text": "Attach an IAM role to the instance with a policy scoped to that bucket"},
                {"key": "C", "text": "Make the bucket public and restrict access by IP address"},
                {"key": "D", "text": "Create an IAM user per instance and rotate the keys weekly"},
            ],
            "correct": "B",
            "explanations": {
                "A": "This stores long-lived credentials on the instance - if the instance is compromised, so are the keys, and this is exactly what the question rules out.",
                "B": "Correct. An IAM role gives the instance short-lived, automatically-rotated credentials, scoped to just that bucket - no keys ever live on disk.",
                "C": "Making a bucket public is a serious exposure risk - IP restriction alone doesn't make this safe, and it's not necessary here.",
                "D": "Per-instance IAM users still means long-lived keys to manage and rotate - roles solve this problem directly.",
            },
        },
        {
            "id": "c4", "category": "IAM & security",
            "text": "You need to give a contractor temporary, read-only access to one project's resources for two weeks. What's the best fit?",
            "options": [
                {"key": "A", "text": "Create a permanent IAM user and delete it manually after two weeks"},
                {"key": "B", "text": "Share your own root account credentials"},
                {"key": "C", "text": "Create an IAM role with a read-only policy and a two-week session limit, and have them assume it"},
                {"key": "D", "text": "Give them full admin access, since it's only temporary"},
            ],
            "correct": "C",
            "explanations": {
                "A": "This works, but relies on someone remembering to delete it - a scoped, time-limited role removes that manual step entirely.",
                "B": "Never share root credentials - it's unscoped, unrevocable per-person, and a serious security risk.",
                "C": "Correct. A role with a defined session length and a read-only policy gives exactly the access needed, for exactly as long as needed, with no standing credentials left behind.",
                "D": "Admin access for read-only work badly violates least privilege, even if it's short-term.",
            },
        },
        {
            "id": "c5", "category": "Cloud architecture",
            "text": "A single-instance app keeps going down under traffic spikes. What's the most direct fix?",
            "options": [
                {"key": "A", "text": "Upgrade to a bigger instance type only"},
                {"key": "B", "text": "Put it behind a load balancer with auto-scaling across multiple instances"},
                {"key": "C", "text": "Add a second internet gateway"},
                {"key": "D", "text": "Move the app to a different region"},
            ],
            "correct": "B",
            "explanations": {
                "A": "A bigger instance raises the ceiling but is still a single point of failure - it'll just fail at a higher traffic number.",
                "B": "Correct. A load balancer with auto-scaling adds capacity automatically as traffic grows, and removes the single point of failure.",
                "C": "A VPC only needs one internet gateway - adding another doesn't affect capacity or availability.",
                "D": "Changing region doesn't address capacity at all - the same single-instance problem would just happen somewhere else.",
            },
        },
        {
            "id": "c6", "category": "Cloud architecture",
            "text": "What's the main benefit of defining infrastructure in Terraform instead of clicking through the console?",
            "options": [
                {"key": "A", "text": "It's the only way to use a cloud provider's free tier"},
                {"key": "B", "text": "Infrastructure becomes reviewable, versioned, and repeatable, like application code"},
                {"key": "C", "text": "It automatically makes infrastructure cheaper"},
                {"key": "D", "text": "It removes the need for IAM permissions"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Free tier access has nothing to do with how infrastructure is provisioned.",
                "B": "Correct. Terraform files can be reviewed, version-controlled, and re-run reliably - the same benefits code review brings to application code.",
                "C": "Terraform doesn't change what resources cost - it changes how reliably and repeatably they're created.",
                "D": "Terraform still needs valid IAM permissions to create anything - it doesn't bypass access control.",
            },
        },
        {
            "id": "c7", "category": "Networking",
            "text": "A single malicious IP needs to be blocked from an entire subnet, including connections that are already open. What's the right tool?",
            "options": [
                {"key": "A", "text": "A security group deny rule"},
                {"key": "B", "text": "A network ACL with an explicit deny for that IP"},
                {"key": "C", "text": "Renaming the subnet"},
                {"key": "D", "text": "A new internet gateway"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Security groups are allow-only and stateful - there's no way to write a deny rule, and they wouldn't affect a connection already in progress.",
                "B": "Correct. Network ACLs are stateless and support explicit deny rules at the subnet level, so they can block a specific IP outright, mid-connection included.",
                "C": "Renaming a subnet has no effect on traffic filtering.",
                "D": "A second internet gateway doesn't filter traffic by source - it's not a security control at all.",
            },
        },
        {
            "id": "c8", "category": "IAM & security",
            "text": "A Lambda function only needs to write logs to one CloudWatch log group. Which policy best follows least privilege?",
            "options": [
                {"key": "A", "text": "AdministratorAccess, so it never hits a permissions error"},
                {"key": "B", "text": "A policy scoped to just the write actions on that specific log group"},
                {"key": "C", "text": "No policy - Lambda works without one"},
                {"key": "D", "text": "ReadOnlyAccess across the whole account"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Administrator access grants far more than logging ever requires - a compromised function would then be able to touch everything in the account.",
                "B": "Correct. A narrowly scoped policy grants exactly the one action, on exactly the one resource, that the function actually needs.",
                "C": "Lambda always needs an execution role - without one it can't even write logs.",
                "D": "Read-only access doesn't include the write permission this function actually needs, and it's still far broader than necessary.",
            },
        },
        {
            "id": "c9", "category": "Cloud architecture",
            "text": "Why should app servers behind a load balancer be kept stateless, with session data stored externally (e.g. in a database or cache)?",
            "options": [
                {"key": "A", "text": "So any server can handle any request, which is what makes horizontal scaling and failover work"},
                {"key": "B", "text": "Because stateless servers are always cheaper to run"},
                {"key": "C", "text": "Because the load balancer requires it to boot"},
                {"key": "D", "text": "It has no real effect on scaling"},
            ],
            "correct": "A",
            "explanations": {
                "A": "Correct. If session data lived only on one server, a user would have to keep hitting that exact server - stateless servers let the load balancer route any request anywhere, so adding or losing a server doesn't break anyone's session.",
                "B": "Cost depends on instance size and count, not statefulness - this isn't the reason.",
                "C": "Load balancers don't require app servers to be stateless to start up.",
                "D": "Statelessness is precisely what makes horizontal scaling and failover practical - it has a direct effect.",
            },
        },
        {
            "id": "c10", "category": "Cloud architecture",
            "text": "A team's cloud bill has grown unexpectedly this month. What's the most direct first step to find out why?",
            "options": [
                {"key": "A", "text": "Guess which service is responsible and shut it down"},
                {"key": "B", "text": "Use the provider's cost/billing explorer to break down spend by service"},
                {"key": "C", "text": "Wait for next month's bill to see if it happens again"},
                {"key": "D", "text": "Delete the whole account and start over"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Shutting down a guessed service risks taking down something that's actually needed, without confirming it's the real cause.",
                "B": "Correct. A cost breakdown by service (and by day) shows exactly where the increase came from, so the fix can target the actual cause.",
                "C": "Waiting doesn't diagnose anything and lets the same overspend repeat.",
                "D": "This is a drastic, irreversible step for what a billing breakdown can usually explain in minutes.",
            },
        },
    ],
    "cyber": [
        {
            "id": "y1", "category": "Networking",
            "text": "A colleague says a firewall alone is enough to secure an internal network. What's the issue with that?",
            "options": [
                {"key": "A", "text": "Firewalls only work on Windows machines"},
                {"key": "B", "text": "A firewall controls traffic at the perimeter but doesn't stop threats already inside the network"},
                {"key": "C", "text": "Firewalls are always disabled by default"},
                {"key": "D", "text": "There's no issue - a firewall is fully sufficient"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Firewalls are platform-independent - this isn't a real limitation.",
                "B": "Correct. Perimeter defence doesn't help once a threat is already inside (a phishing click, a compromised laptop) - that's why layered controls like segmentation and monitoring matter too.",
                "C": "Default state varies by vendor and isn't the point of the question.",
                "D": "Relying on one layer of defence is exactly the risky assumption being asked about here.",
            },
        },
        {
            "id": "y2", "category": "Networking",
            "text": "What does network segmentation primarily protect against?",
            "options": [
                {"key": "A", "text": "Slow internet speeds"},
                {"key": "B", "text": "A breach in one part of the network spreading freely to every other part"},
                {"key": "C", "text": "Hardware failure"},
                {"key": "D", "text": "Password reuse"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Segmentation is a security control, not a performance optimisation.",
                "B": "Correct. Splitting a network into zones limits how far an attacker can move once they've gained a foothold in one segment.",
                "C": "Hardware redundancy, not segmentation, is what protects against hardware failure.",
                "D": "Password reuse is addressed by credential policy and MFA, not network design.",
            },
        },
        {
            "id": "y3", "category": "Identity & access",
            "text": "Why is multi-factor authentication considered a major security improvement over a password alone?",
            "options": [
                {"key": "A", "text": "It makes passwords unnecessary"},
                {"key": "B", "text": "It requires a second, independent factor, so a stolen password alone isn't enough to log in"},
                {"key": "C", "text": "It automatically blocks all phishing emails"},
                {"key": "D", "text": "It makes the login page load faster"},
            ],
            "correct": "B",
            "explanations": {
                "A": "MFA adds a second factor on top of a password - it doesn't remove the password requirement.",
                "B": "Correct. Even if a password is leaked or phished, an attacker still needs the second factor (a device, a code, a key) to get in.",
                "C": "MFA doesn't filter email - that's a separate control entirely.",
                "D": "MFA has no effect on page load speed.",
            },
        },
        {
            "id": "y4", "category": "Identity & access",
            "text": "An employee leaves the company. What's the correct first step from a security standpoint?",
            "options": [
                {"key": "A", "text": "Wait until the next scheduled access review"},
                {"key": "B", "text": "Revoke their account access and credentials immediately"},
                {"key": "C", "text": "Just change the shared team password"},
                {"key": "D", "text": "Leave access active in case they return"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Waiting leaves a valid, unmonitored account active - that's a real exposure window, not a minor delay.",
                "B": "Correct. Immediate revocation is standard offboarding practice precisely because delayed deprovisioning is a common real-world breach source.",
                "C": "A shared password doesn't address the individual's personal account access at all.",
                "D": "Leaving access active for a former employee is a significant, avoidable risk.",
            },
        },
        {
            "id": "y5", "category": "Security fundamentals",
            "text": "What's the main difference between encryption at rest and encryption in transit?",
            "options": [
                {"key": "A", "text": "There's no real difference, they're the same thing"},
                {"key": "B", "text": "At rest protects stored data; in transit protects data as it moves across a network"},
                {"key": "C", "text": "At rest is only for cloud storage; in transit is only for email"},
                {"key": "D", "text": "In transit is always weaker than at rest"},
            ],
            "correct": "B",
            "explanations": {
                "A": "They protect data in different states and typically use different mechanisms - they're not interchangeable.",
                "B": "Correct. Encryption at rest protects data sitting on disk; encryption in transit (like TLS) protects data while it's being sent - a system usually needs both.",
                "C": "Both apply broadly, not to those specific narrow cases.",
                "D": "Strength depends on the algorithm and implementation, not on which state is being protected.",
            },
        },
        {
            "id": "y6", "category": "Security fundamentals",
            "text": "A user reports a suspicious email asking them to reset their password via a link. What should they do first?",
            "options": [
                {"key": "A", "text": "Click the link to check if it's real"},
                {"key": "B", "text": "Reply to the email asking who sent it"},
                {"key": "C", "text": "Avoid the link, and verify through a known, separate channel (like typing the site's real URL directly)"},
                {"key": "D", "text": "Forward it to friends to see if they got it too"},
            ],
            "correct": "C",
            "explanations": {
                "A": "Clicking an unverified link is exactly the action a phishing attempt is trying to get - even 'just checking' can trigger credential theft.",
                "B": "Replying confirms to an attacker that the address is active and being read, and doesn't verify anything.",
                "C": "Correct. Going to the real site directly (not through the email's link) is the safe way to check if the request is genuine.",
                "D": "Forwarding a suspicious email spreads the risk instead of containing it.",
            },
        },
        {
            "id": "y7", "category": "Networking",
            "text": "An employee connects to work systems from public café Wi-Fi using a VPN. What is the VPN primarily protecting here?",
            "options": [
                {"key": "A", "text": "It makes the café Wi-Fi itself secure for everyone using it"},
                {"key": "B", "text": "It encrypts traffic between the device and the corporate network, so others on that Wi-Fi can't read it"},
                {"key": "C", "text": "It speeds up the connection"},
                {"key": "D", "text": "It replaces the need for a password"},
            ],
            "correct": "B",
            "explanations": {
                "A": "The VPN only protects its own user's traffic - it does nothing for the security of the shared network itself.",
                "B": "Correct. Public Wi-Fi is easy to eavesdrop on; a VPN tunnels and encrypts traffic on that link so someone else on the same network can't read it.",
                "C": "A VPN typically adds a small amount of overhead - speed isn't the reason to use one here.",
                "D": "A VPN is a separate layer entirely - it doesn't remove the need to authenticate.",
            },
        },
        {
            "id": "y8", "category": "Identity & access",
            "text": "What's the main risk of reusing the same password across multiple accounts?",
            "options": [
                {"key": "A", "text": "It makes the password harder to remember"},
                {"key": "B", "text": "A breach of one weaker site leaks a password that then works to log into your other accounts"},
                {"key": "C", "text": "Websites process reused passwords slower"},
                {"key": "D", "text": "There is no real risk if the password is long"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Memorability is a convenience issue, not the security risk being asked about here.",
                "B": "Correct. Attackers routinely test leaked email/password pairs against other sites - a breach anywhere the password was reused becomes a breach everywhere it was reused.",
                "C": "Password reuse has no effect on server-side processing speed.",
                "D": "Length helps resist guessing, but it does nothing once the exact password has already leaked in plain or crackable form from another breach.",
            },
        },
        {
            "id": "y9", "category": "Security fundamentals",
            "text": "What's the purpose of having an incident response plan in place before a breach happens?",
            "options": [
                {"key": "A", "text": "It guarantees a breach will never happen"},
                {"key": "B", "text": "It gives the team clear, rehearsed steps to detect, contain and recover, instead of improvising under pressure"},
                {"key": "C", "text": "It's only a legal formality with no practical use"},
                {"key": "D", "text": "It replaces the need for backups"},
            ],
            "correct": "B",
            "explanations": {
                "A": "No plan can prevent every breach - the plan is about the response, not prevention.",
                "B": "Correct. A tested plan means the team already knows who does what, so containment starts in minutes instead of being figured out live during the incident.",
                "C": "It has real operational value during an actual incident, well beyond paperwork.",
                "D": "Backups are a separate control - a response plan usually references them, but doesn't replace them.",
            },
        },
        {
            "id": "y10", "category": "Security fundamentals",
            "text": "Why do organisations patch software on a regular schedule instead of only when something breaks?",
            "options": [
                {"key": "A", "text": "Patching is mainly to add new features"},
                {"key": "B", "text": "To fix known vulnerabilities before attackers have a chance to exploit them"},
                {"key": "C", "text": "Vendors require it for warranty reasons only"},
                {"key": "D", "text": "Unpatched software runs faster, so patching is a trade-off with no security benefit"},
            ],
            "correct": "B",
            "explanations": {
                "A": "Patches sometimes include features, but security patches specifically exist to close known holes.",
                "B": "Correct. Once a vulnerability is public, attackers actively scan for systems that haven't patched it yet - regular patching closes that window.",
                "C": "Warranty terms aren't the security reason patch cadences exist.",
                "D": "Patching isn't primarily about performance, and this option gets the trade-off backwards - unpatched systems carry the real risk.",
            },
        },
    ],
}

RECOMMENDATIONS = [
    {"provider": "HC", "title": "Terraform Associate", "meta": "4 weeks - closes 2 gaps - ₹6,200", "tag": "Best fit"},
    {"provider": "AWS", "title": "Solutions Architect - Associate", "meta": "8 weeks - closes 3 gaps - ₹12,700", "tag": "Week 5"},
]

# --- Profile screen ---

PROFILE_STEPS = [
    {"label": "Personal details", "status": "done"},
    {"label": "Education", "status": "done"},
    {"label": "Skills & certifications", "status": "current"},
    {"label": "Projects", "status": "pending"},
    {"label": "Internship", "status": "pending"},
    {"label": "Resume & links", "status": "pending"},
    {"label": "Preview profile", "status": "pending"},
]

EDUCATION = [
    {"level": "B.E. Computer Engineering", "meta": "2023 - 2027 - Sem 6 - No backlogs", "score": "8.24"},
    {"level": "HSC - Science", "meta": "2023", "score": "88%"},
]

SKILLS = [
    {"name": "Python", "level": 4},
    {"name": "Networking", "level": 4},
    {"name": "Linux", "level": 3},
    {"name": "AWS core", "level": 2},
    {"name": "Terraform", "level": 1, "warning": True},
]

CERTIFICATIONS_HELD = [
    {"badge": "AWS", "name": "Cloud Practitioner", "meta": "Amazon - Mar 2026", "status": "Verified"},
    {"badge": "CSC", "name": "CCNA", "meta": "Cisco - Nov 2025", "status": "Verified"},
]

PROJECTS = [
    {"title": "Campus bus tracker", "meta": "Team of 3",
     "desc": "Live GPS tracking with a Flask backend and a Postgres store, deployed on a single EC2 instance.",
     "tags": ["Python", "Flask", "AWS EC2"]},
]

RESUME = {"filename": "Aarav_Deshpande_v2.pdf", "meta": "Parsed - 26 Jul - 214 KB", "score": 68}

# --- Skill gap screen ---

SKILL_GAP_ROWS = [
    {"skill": "Terraform / IaC", "asked": "61 of 74 postings", "required": "Level 3", "have": "Level 0",
     "priority": "High", "action": "Terraform Associate track, weeks 3-5", "impact": -7.3},
    {"skill": "AWS IAM & security", "asked": "58 of 74 postings", "required": "Level 3", "have": "Level 1",
     "priority": "High", "action": "AWS Solutions Architect - Associate", "impact": -4.8},
    {"skill": "Containers / K8s", "asked": "44 of 74 postings", "required": "Level 2", "have": "Level 1",
     "priority": "Medium", "action": "Docker fundamentals, then a single-node cluster", "impact": -3.1},
    {"skill": "Shell scripting", "asked": "Not in curriculum", "required": "Level 2", "have": "Level 1",
     "priority": "Medium", "action": "Self-study, week 2 of the roadmap", "impact": -1.9},
    {"skill": "CI/CD pipelines", "asked": "31 of 74 postings", "required": "Level 2", "have": "Level 1",
     "priority": "Medium", "action": "Build one pipeline on the bus-tracker project", "impact": -1.6},
    {"skill": "Linux admin", "asked": "71 of 74 postings", "required": "Level 2", "have": "Level 3",
     "priority": "Met", "action": "Nothing needed", "impact": 0.0},
    {"skill": "Networking", "asked": "71 of 74 postings", "required": "Level 2", "have": "Level 3",
     "priority": "Met", "action": "Nothing needed", "impact": 0.0},
]

RADAR_ROLE = {
    "categories": ["Networking", "Linux", "Python", "Containers", "IaC", "AWS security"],
    "you": [4, 4, 4, 2, 0, 1],
    "role_requires": [3, 3, 2, 2, 3, 3],
}

# --- Learning roadmap ---

ROADMAP_PHASES = [
    {"title": "Foundation", "weeks": "Week 1-4", "status": "In progress",
     "desc": "Linux, shell scripting, then your first Terraform files. None of this costs anything to run.",
     "progress": 55},
    {"title": "Core cloud skills", "weeks": "Week 5-8", "status": "Upcoming",
     "desc": "AWS IAM and networking properly, containers from Docker up to a single-node cluster.",
     "progress": 0},
    {"title": "Job-ready & cert prep", "weeks": "Week 9-12", "status": "Upcoming",
     "desc": "CI/CD on your own project, then four weeks of AWS SAA preparation and mock exams.",
     "progress": 0},
]

ROADMAP_TIMELINE = [
    {"track": "Linux & shell", "start_week": 1, "end_week": 3, "status": "done"},
    {"track": "Terraform / IaC", "start_week": 3, "end_week": 5, "status": "now"},
    {"track": "AWS IAM & security", "start_week": 5, "end_week": 7, "status": "upcoming"},
    {"track": "Containers / K8s", "start_week": 7, "end_week": 9, "status": "upcoming"},
    {"track": "CI/CD pipelines", "start_week": 9, "end_week": 10, "status": "upcoming"},
    {"track": "AWS SAA prep", "start_week": 10, "end_week": 12, "status": "upcoming"},
]

THIS_WEEK = [
    {"title": "Terraform providers & state", "meta": "2 readings - 1 lab - checkpoint quiz", "status": "active"},
    {"title": "Week 2 - Shell scripting basics", "meta": "", "status": "done"},
    {"title": "Week 4 - Modules, remote state, a small VPC", "meta": "", "status": "next"},
]

# --- Certifications ---

CERT_RECOMMENDATIONS = [
    {"provider": "AWS", "vendor": "Amazon", "rank": 1, "match": 0.91, "name": "Solutions Architect - Associate",
     "level": "Intermediate", "duration": "8 weeks", "cost": "₹12,700", "rating": 4.8,
     "gaps_closed": "3 of 7", "uplift": "+9 points", "asked_in": "38 of 74 roles",
     "skills": ["AWS IAM", "Networking", "Architecture"]},
    {"provider": "HC", "vendor": "HashiCorp", "rank": 2, "match": 0.83, "name": "Terraform Associate",
     "level": "Beginner", "duration": "4 weeks", "cost": "₹6,200", "rating": None,
     "gaps_closed": "2 of 7", "uplift": "+6 points", "asked_in": "24 of 74 roles", "skills": []},
    {"provider": "CNF", "vendor": "CNCF", "rank": 3, "match": 0.77, "name": "Certified Kubernetes Administrator",
     "level": "Advanced", "duration": "12 weeks", "cost": "₹33,000", "rating": None,
     "gaps_closed": "2 of 7", "uplift": "+7 points", "asked_in": "19 of 74 roles", "skills": []},
]

CERT_TABLE = [
    {"name": "Solutions Architect - Associate", "provider": "Amazon", "level": "Intermediate",
     "duration": "8 weeks", "cost": "₹12,700", "uplift": "+9"},
    {"name": "Terraform Associate", "provider": "HashiCorp", "level": "Beginner",
     "duration": "4 weeks", "cost": "₹6,200", "uplift": "+6"},
    {"name": "Certified Kubernetes Administrator", "provider": "CNCF", "level": "Advanced",
     "duration": "12 weeks", "cost": "₹33,000", "uplift": "+7"},
    {"name": "Azure Fundamentals", "provider": "Microsoft", "level": "Beginner",
     "duration": "3 weeks", "cost": "₹3,800", "uplift": "+3"},
    {"name": "Cloud Practitioner", "provider": "Amazon", "level": "Beginner",
     "duration": "-", "cost": "-", "uplift": "held"},
]

# --- Career suggestions ---

CAREER_MATCHES = [
    {"role": "Cloud Support Associate", "match": 86, "status": "Ready now",
     "skills_ok": ["Linux", "Networking", "Python"], "skills_gap": ["AWS depth", "IaC"],
     "salary": "₹5.2 - 7.0 LPA", "hiring": "TCS, Rackspace, Zensar", "openings": 23},
    {"role": "Cloud Ops / DevOps Trainee", "match": 74, "status": "2 gaps away",
     "skills_ok": ["Linux", "Python"], "skills_gap": ["Terraform", "CI/CD", "Containers"],
     "salary": "₹6.5 - 9.0 LPA", "hiring": "Infosys, Persistent, Quest", "openings": 17},
    {"role": "SOC Analyst L1", "match": 61, "status": "Stretch",
     "skills_ok": ["Networking"], "skills_gap": ["SIEM", "Incident handling", "Log analysis"],
     "salary": "₹4.8 - 6.5 LPA", "hiring": "Wipro, Deloitte, LTIMindtree", "openings": 11},
]

FIT_BREAKDOWN = [
    {"label": "Skills match", "value": 88},
    {"label": "Academic fit", "value": 82},
    {"label": "Project evidence", "value": 79},
    {"label": "Certification match", "value": 50},
]

ROLE_REQUIREMENTS = [
    {"item": "Linux and networking fundamentals", "asked": "71 of 74", "status": "Met"},
    {"item": "One cloud provider at associate depth", "asked": "68 of 74", "status": "Partial"},
    {"item": "Scripting for automation", "asked": "55 of 74", "status": "Partial"},
    {"item": "Ticketing and customer communication", "asked": "49 of 74", "status": "Met"},
    {"item": "Infrastructure as code exposure", "asked": "41 of 74", "status": "Gap"},
    {"item": "A named cloud certification", "asked": "38 of 74", "status": "Partial"},
]

# --- Analytics ---

ANALYTICS_SUMMARY = [
    {"label": "Assessments taken", "value": "6", "delta": "+2"},
    {"label": "Average performance", "value": "76%", "delta": "+9%"},
    {"label": "Learning hours", "value": "18", "delta": "Target 24"},
    {"label": "Skills improved", "value": "4 of 11", "delta": ""},
]

SECTION_PERFORMANCE = [
    {"section": "Technical", "score": 82},
    {"section": "Aptitude", "score": 71},
    {"section": "Comms", "score": 66},
    {"section": "Resume", "score": 68},
    {"section": "Certs", "score": 48},
]

HOURS_LOGGED = [
    {"month": "May", "hours": 26, "target": 24, "met": True},
    {"month": "June", "hours": 24, "target": 24, "met": True},
    {"month": "July", "hours": 18, "target": 24, "met": False},
]

SKILL_PRACTICE_HEATMAP = {
    "skills": ["Linux", "Python", "Networking", "AWS", "Terraform", "Containers"],
    "months": ["Feb", "Mar", "Apr", "May", "Jun", "Jul"],
    "matrix": [
        [1, 2, 2, 3, 2, 1],
        [2, 3, 1, 0, 0, 0],
        [3, 2, 1, 1, 1, 0],
        [0, 0, 1, 2, 3, 2],
        [0, 0, 0, 1, 2, 3],
        [0, 0, 0, 0, 1, 1],
    ],
}

ATTEMPT_HISTORY = [
    {"name": "Technical - Cloud", "when": "28 Jul - attempt 2", "score": "82%", "kind": "success"},
    {"name": "Aptitude", "when": "28 Jul - attempt 1", "score": "71%", "kind": "success"},
    {"name": "Technical - Cloud", "when": "14 Jun - attempt 1", "score": "64%", "kind": "warning"},
    {"name": "Resume review", "when": "26 Jul - v2", "score": "68%", "kind": "success"},
    {"name": "Communication", "when": "In progress", "score": "6/15", "kind": "warning"},
]

# --- Reports ---

REPORT_CONTENTS = [
    {"item": "Employability score and components", "included": True},
    {"item": "Skill gap table", "included": True},
    {"item": "Learning roadmap", "included": True},
    {"item": "Assessment answer sheet", "included": False},
    {"item": "Cohort comparison", "included": False},
]

REPORT_HISTORY = [
    {"name": "Full employability report", "when": "31 Jul 2026, 4:14 PM", "score": 74, "size": "1.2 MB"},
    {"name": "Progress report", "when": "30 Jun 2026", "score": 68, "size": "640 KB"},
    {"name": "Full employability report", "when": "14 Jun 2026", "score": 64, "size": "1.1 MB"},
    {"name": "Skill gap summary", "when": "02 May 2026", "score": 58, "size": "420 KB"},
]

# --- Streak / level / achievements (fun restyle, 24 Sep) ---
# Small "delight" data for the dashboard's streak chip and achievement
# badges. Purely motivational, not part of the employability score itself.

STREAK = {
    "days": 3,
    "level": 4,
    "level_title": "Explorer",
    "xp": 320,
    "xp_next_level": 500,
}

ACHIEVEMENTS = [
    {"key": "first_assessment", "label": "First assessment", "icon": "assessment", "unlocked": True, "status": "Completed"},
    {"key": "first_cert", "label": "First certification", "icon": "certifications", "unlocked": True, "status": "Completed"},
    {"key": "streak_3", "label": "3-day streak", "icon": "zap", "unlocked": True, "status": "Completed"},
    {"key": "profile_100", "label": "Profile 100%", "icon": "profile", "unlocked": False, "status": "In progress"},
    {"key": "job_ready", "label": "Job-ready score", "icon": "trend", "unlocked": False, "status": "Locked"},
]


# --- Derived values -------------------------------------------------------
# Anything a screen shows that can be computed from the data above is
# computed here once, so the same number appears on every page (score,
# profile completion, gaps, certifications, projects, learning progress).

OPEN_GAPS = sum(1 for r in SKILL_GAP_ROWS if r["priority"] != "Met")
HIGH_GAPS = sum(1 for r in SKILL_GAP_ROWS if r["priority"] == "High")
MET_GAPS = sum(1 for r in SKILL_GAP_ROWS if r["priority"] == "Met")
TOTAL_SKILL_ROWS = len(SKILL_GAP_ROWS)

PROJECTS_TARGET = 3
CERTS_HELD_COUNT = len(CERTIFICATIONS_HELD)

PROJECTED_SCORE = 88
POINTS_TO_JOB_READY = SCORE["job_ready_threshold"] - SCORE["overall"]
VS_COHORT = round(SCORE["overall"] - SCORE["cohort_average"], 1)

ROADMAP_TOTAL_WEEKS = 12
ROADMAP_CURRENT_WEEK = 3
ROADMAP_PROGRESS_PCT = 22

# The latest report always reflects the current score.
REPORT_HISTORY[0]["score"] = SCORE["overall"]
# Score history ends on the current score.
SCORE_HISTORY["student"][-1] = SCORE["overall"]
