"""
NetSage AI — Database Seeder
Seeds the database with 35 realistic troubleshooting cases and responsible AI log entries.
"""

import csv
import os
import json
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import get_db, init_db

DATASET_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dataset", "cases.csv")

# Responsible AI log entries — cases where AI was corrected by a human
RESPONSIBLE_AI_ENTRIES = [
    {
        "case_id": "CASE-003",
        "ai_diagnosis": "Router interface Gig0/0 is down, causing connectivity failure.",
        "human_correction": "The router interface is up. The actual issue is that the PC's default gateway (10.10.20.1) is on a different subnet than the PC's IP (10.10.10.10/24).",
        "why_ai_wrong": "The AI focused on a potential interface issue without carefully checking the ipconfig output. The gateway 10.10.20.1 is clearly outside the 10.10.10.0/24 subnet, which the AI overlooked.",
        "final_diagnosis": "Incorrect default gateway configuration on PC. Gateway 10.10.20.1 is not in the PC's subnet 10.10.10.0/24. Should be 10.10.10.1.",
        "lesson": "Always verify IP addressing and subnet relationships before assuming physical layer issues. A gateway mismatch is a common misconfiguration that is easy to overlook."
    },
    {
        "case_id": "CASE-005",
        "ai_diagnosis": "DHCP server is not running or the DHCP process has crashed on the router.",
        "human_correction": "The DHCP server is running and the pool is correctly configured. The issue is that the excluded-address range (192.168.1.1 to 192.168.1.254) covers the entire address pool, leaving no addresses for clients.",
        "why_ai_wrong": "The AI assumed a service-level failure without examining the DHCP configuration details. The excluded-address range is a subtle but critical detail that requires careful comparison with the pool's network statement.",
        "final_diagnosis": "DHCP excluded-address range 192.168.1.1-192.168.1.254 covers all usable addresses in the 192.168.1.0/24 pool. No addresses remain for dynamic assignment.",
        "lesson": "When DHCP is not assigning addresses, always compare the excluded-address range against the pool network. The overlap between exclusions and the pool is a frequent source of DHCP failures."
    },
    {
        "case_id": "CASE-009",
        "ai_diagnosis": "Routing issue between VLAN 10 and VLAN 30. Missing route to 10.10.30.0/24 on the router.",
        "human_correction": "The route exists and ping to 10.10.30.100 succeeds (ICMP works). The actual issue is ACL 101 which explicitly denies TCP port 80 (HTTP) from 10.10.10.0/24 to 10.10.30.100. This is a Layer 4 issue, not Layer 3.",
        "why_ai_wrong": "The AI defaulted to a routing diagnosis without checking the ACL configuration. The fact that ping works but HTTP doesn't is a strong indicator of an ACL or firewall issue at Layer 4, not a routing problem at Layer 3.",
        "final_diagnosis": "ACL 101 line 10 denies TCP traffic from 10.10.10.0/24 to 10.10.30.100 on port 80 (www). This blocks HTTP while allowing ICMP (ping) to succeed.",
        "lesson": "When ping works but a specific application fails, suspect ACL or firewall rules at Layer 4. Don't assume routing problems when ICMP connectivity is proven."
    },
    {
        "case_id": "CASE-020",
        "ai_diagnosis": "Wireless SSID is not broadcasting or the AP is not functioning correctly.",
        "human_correction": "The wireless network is working. The security issue is that guest WiFi users (VLAN 50) can access the internal file server (10.10.30.50 on VLAN 30). There is no ACL on the guest VLAN interface to enforce isolation.",
        "why_ai_wrong": "The AI interpreted the symptom incorrectly. The problem is not that WiFi isn't working — it's that it works too well, allowing guest users to reach internal resources. The AI failed to recognize this as a security/isolation problem.",
        "final_diagnosis": "Guest VLAN 50 subinterface has no inbound ACL. No access control prevents guest-to-internal routing. An ACL must be applied to deny guest traffic to internal VLANs while permitting internet access.",
        "lesson": "Not all network problems are about connectivity failure. Security violations where too much access is granted are equally critical. Always consider whether the problem is too little access or too much access."
    },
    {
        "case_id": "CASE-013",
        "ai_diagnosis": "STP convergence issue causing intermittent connectivity. One of the switches has a suboptimal root bridge election.",
        "human_correction": "While STP could contribute, the primary issue is a native VLAN mismatch on the trunk link. SW1 uses native VLAN 1 and SW2 uses native VLAN 99. The CDP error message explicitly states this mismatch.",
        "why_ai_wrong": "The AI recognized a Layer 2 issue but focused on STP instead of the explicit CDP warning about native VLAN mismatch. The log message '%CDP-4-NATIVE_VLAN_MISMATCH' is direct evidence that should have been the primary finding.",
        "final_diagnosis": "Native VLAN mismatch: SW1 trunk Fa0/24 uses native VLAN 1, SW2 trunk Fa0/24 uses native VLAN 99. This causes frames to be tagged/untagged incorrectly, leading to intermittent connectivity.",
        "lesson": "Always check log messages and warnings in the show output. Explicit error messages like CDP native VLAN mismatch warnings are stronger evidence than inferred issues."
    }
]


async def seed_database():
    """Seed the database with cases from the CSV and responsible AI log entries."""
    await init_db()

    db = await get_db()
    try:
        # Check if data already exists
        cursor = await db.execute("SELECT COUNT(*) as count FROM cases")
        row = await cursor.fetchone()
        if dict(row)["count"] > 0:
            print("Database already seeded. Skipping.")
            await db.close()
            return

        # Read and insert cases from CSV
        if not os.path.exists(DATASET_PATH):
            print(f"Dataset file not found: {DATASET_PATH}")
            await db.close()
            return

        with open(DATASET_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row_data in reader:
                case_id = f"CASE-{int(row_data['case_id']):03d}"
                await db.execute(
                    """INSERT INTO cases (case_id, title, symptom, topology_notes, show_outputs, 
                       expected_fault, osi_layer, concept, severity, status)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        case_id,
                        row_data['title'],
                        row_data['symptom'],
                        row_data['topology_notes'],
                        row_data['show_outputs'],
                        row_data['expected_fault'],
                        row_data['osi_layer'],
                        row_data['concept'],
                        row_data['severity'],
                        'Open'
                    )
                )
                count += 1

        print(f"Inserted {count} cases.")

        # Insert responsible AI log entries
        for entry in RESPONSIBLE_AI_ENTRIES:
            await db.execute(
                """INSERT INTO responsible_ai_log 
                   (case_id, ai_diagnosis, human_correction, why_ai_wrong, final_diagnosis, lesson)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    entry["case_id"],
                    entry["ai_diagnosis"],
                    entry["human_correction"],
                    entry["why_ai_wrong"],
                    entry["final_diagnosis"],
                    entry["lesson"]
                )
            )

        print(f"Inserted {len(RESPONSIBLE_AI_ENTRIES)} responsible AI log entries.")

        # Pre-populate some reviews for demo purposes
        demo_reviews = [
            ("CASE-001", "PC is assigned to VLAN 20 instead of VLAN 10", 92, "Layer 2", "accepted", "", "Correct diagnosis - VLAN assignment was wrong"),
            ("CASE-003", "Router interface is down", 70, "Layer 1", "edited", "Incorrect default gateway, not interface issue", "AI incorrectly blamed the interface instead of checking the gateway configuration"),
            ("CASE-005", "DHCP server not running", 60, "Layer 7", "rejected", "", "DHCP server is running. The excluded-address range covers the entire pool."),
            ("CASE-007", "Missing static route to 172.16.0.0/16", 88, "Layer 3", "accepted", "", "Correct - no route exists in the routing table"),
            ("CASE-009", "Routing issue between VLANs", 65, "Layer 3", "edited", "ACL blocking HTTP, not routing issue", "Ping works so routing is fine. ACL 101 denies HTTP specifically."),
            ("CASE-013", "STP convergence issue", 55, "Layer 2", "rejected", "", "Native VLAN mismatch is the primary issue, not STP"),
            ("CASE-020", "SSID not broadcasting", 40, "Layer 2", "rejected", "", "WiFi works - the problem is guest isolation failure"),
            ("CASE-002", "VLAN 30 not allowed on trunk", 95, "Layer 2", "accepted", "", "Spot on diagnosis"),
            ("CASE-008", "OSPF area mismatch", 90, "Layer 3", "accepted", "", "Correctly identified area mismatch between R1 and R2"),
            ("CASE-010", "NAT inside/outside not configured", 85, "Layer 3", "accepted", "", "Correct - ip nat inside/outside missing from interfaces"),
        ]

        for case_id, root_cause, confidence, osi_layer, decision, edited, notes in demo_reviews:
            # Insert diagnosis
            cursor = await db.execute(
                """INSERT INTO diagnoses (case_id, root_cause, confidence, osi_layer, evidence, next_command, fix_steps, alternative_causes, is_demo_mode)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)""",
                (case_id, root_cause, confidence, osi_layer, '[]', 'show ip interface brief', '[]', '[]')
            )
            diag_id = cursor.lastrowid

            # Insert review
            await db.execute(
                """INSERT INTO reviews (case_id, diagnosis_id, decision, edited_diagnosis, reviewer_notes)
                   VALUES (?, ?, ?, ?, ?)""",
                (case_id, diag_id, decision, edited, notes)
            )

            # Update case status
            status_map = {"accepted": "Resolved", "edited": "Resolved", "rejected": "Open"}
            await db.execute(
                "UPDATE cases SET status = ? WHERE case_id = ?",
                (status_map.get(decision, "Open"), case_id)
            )

        print(f"Inserted {len(demo_reviews)} demo reviews.")

        await db.commit()
        print("Database seeding complete!")

    finally:
        await db.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_database())
