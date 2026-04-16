from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    intent: str
    key_facts: tuple[str, ...]
    tone: str
    reference_email: str


SCENARIOS: list[Scenario] = [
    Scenario(
        id="S01-formal-board-feedback",
        intent="Request written feedback from attendees of the Q1 board meeting",
        key_facts=(
            "Board meeting was held on April 3rd",
            "Discussed FY26 strategic plan and hiring freeze",
            "Need feedback by April 18th for next steps memo",
            "Responses should be emailed to the Chief of Staff",
        ),
        tone="formal",
        reference_email="""Subject: Q1 Board Meeting — Feedback Request

Dear Board Members,

Thank you for joining the Q1 board meeting on April 3rd. The discussion on our FY26 plan and the proposed hiring freeze was a valuable one.

I would like to include your written feedback in the next steps memo. If you have concerns, questions, or points you want captured, please share them.

Kindly send your responses to the Chief of Staff by April 18th. Happy to provide more context or materials if it helps.

Best regards,
[Your Name]""",
    ),
    Scenario(
        id="S02-casual-lunch-invite",
        intent="Invite a coworker to lunch to discuss a new cross-team project",
        key_facts=(
            "Want to grab lunch this Thursday or Friday",
            "Discussing the new analytics integration project",
            "Prefer somewhere close to the office",
            "Happy to put it on the team card",
        ),
        tone="casual",
        reference_email="""Subject: Lunch this week?

Hey,

Want to grab lunch this Thursday or Friday? I'd like to talk through the new analytics integration project before things really kick off.

Somewhere close to the office would be great so we don't spend half the break walking. I'll put it on the team card.

Let me know which day works.

Cheers,
[Your Name]""",
    ),
    Scenario(
        id="S03-urgent-sla-miss",
        intent="Inform a key client that we missed an SLA and outline the recovery plan",
        key_facts=(
            "Missed the 4-hour response SLA on ticket #88421 by 90 minutes",
            "Root cause was a paging misconfiguration, now corrected",
            "Offering a 10% service credit for the month",
            "Executive sponsor will call the client within 24 hours",
        ),
        tone="urgent",
        reference_email="""Subject: Missed SLA on #88421 — here's the plan

Hi [Client],

Getting ahead of this — we missed the 4-hour response SLA on ticket #88421 by 90 minutes. That's on us.

The cause was a paging misconfiguration. It's fixed and verified, and a full postmortem is underway.

To make it right, we're issuing a 10% service credit for the month. Our executive sponsor will call you within the next 24 hours to walk through the incident.

Happy to talk sooner if you'd like.

Regards,
[Your Name]""",
    ),
    Scenario(
        id="S04-empathetic-condolence",
        intent="Send condolences to a colleague whose father passed away",
        key_facts=(
            "Colleague is Priya on the design team",
            "Her father passed away last weekend",
            "Team is covering her projects while she is out",
            "Offering to bring dinner for her family later this week",
        ),
        tone="empathetic",
        reference_email="""Subject: Thinking of you

Dear Priya,

I was so sorry to hear about your father last weekend. You and your family are in my thoughts.

Please don't worry about work — the design team has your projects covered, and we'll keep things moving until you're ready to come back. Take all the time you need.

If it would help, I'd love to drop off dinner for you and your family later this week. No need to reply — I'll follow up with a time.

Sending love to you all.

With care,
[Your Name]""",
    ),
    Scenario(
        id="S05-formal-candidate-rejection",
        intent="Inform a final-round candidate that they were not selected for the role",
        key_facts=(
            "Candidate is applying for the Senior Backend Engineer role",
            "They completed four rounds including a system design interview",
            "Another candidate was selected, decision was very close",
            "Would like to keep them in mind for future openings",
        ),
        tone="formal",
        reference_email="""Subject: Update on Senior Backend Engineer Role

Dear [Candidate Name],

Thank you for the time you put into our Senior Backend Engineer interview — all four rounds, including the system design conversation. We really enjoyed meeting you.

After a lot of thought, we've decided to move forward with another candidate. I want to be honest — it was a very close call, and your background made the decision a hard one.

We would like to stay in touch about future roles that fit your strengths. If you're open to it, I'll reach out when something relevant comes up.

Thank you again, and I wish you the best in your search.

Sincerely,
[Your Name]""",
    ),
    Scenario(
        id="S06-casual-team-photo",
        intent="Remind the team about the quarterly team photo day",
        key_facts=(
            "Photo day is next Wednesday at 2 PM in the lobby",
            "Wear something non-white (shows up badly on camera)",
            "Whole thing should take about 20 minutes",
            "Remote folks can send in a headshot by Friday",
        ),
        tone="casual",
        reference_email="""Subject: Team photo — next Wednesday 2 PM

Hey team,

Quick reminder — quarterly team photo is next Wednesday at 2 PM in the lobby. Should only take about 20 minutes, so it won't eat your afternoon.

One favour: please don't wear white. It shows up badly on camera and the photographer will thank us.

Remote folks, you're off the hook for the group shot, but please send me a headshot by Friday so we can add you to the roster page.

Thanks,
[Your Name]""",
    ),
    Scenario(
        id="S07-urgent-security-incident",
        intent="Alert stakeholders about a suspicious login event and mandatory password reset",
        key_facts=(
            "Unusual login detected on the admin console at 2:14 AM",
            "Source IP geolocated outside normal employee regions",
            "All admin users must rotate passwords and MFA tokens before 12 PM",
            "Security team is running a full audit and will brief leadership at 3 PM",
        ),
        tone="urgent",
        reference_email="""Subject: ACTION — Admin password rotation by 12 PM today

Team,

At 2:14 AM we saw an unusual login on the admin console from an IP outside our normal regions. We're treating this as a possible compromise until proven otherwise.

All admin users must rotate passwords and MFA tokens before 12 PM today. No exceptions.

Security is running a full audit of recent admin activity and will brief leadership at 3 PM. If you notice anything off on your account, post in #security-incidents right away.

Act now, ask questions after.

Thanks,
[Your Name]""",
    ),
    Scenario(
        id="S08-empathetic-wedding-decline",
        intent="Decline a close friend's wedding invitation due to a family conflict",
        key_facts=(
            "Wedding is on June 14th in Savannah",
            "My sister's 50th birthday gathering is the same weekend",
            "Would love to celebrate with them in another way",
            "Sending a gift from their registry",
        ),
        tone="empathetic",
        reference_email="""Subject: About June 14th

Dear [Friend],

I've been putting off writing this because I'm genuinely sad to send it. I won't be able to make the wedding on June 14th in Savannah — it falls on the same weekend as my sister's 50th birthday, and after a lot of back and forth, I need to be there for her.

This is not a small thing for me. I'd love to celebrate with you another way — dinner once you're back from the honeymoon, or a weekend visit whenever works for you.

A gift from your registry is on its way. Wishing you both the most beautiful day.

All my love,
[Your Name]""",
    ),
    Scenario(
        id="S09-formal-recommendation-request",
        intent="Ask a former professor for a recommendation letter for an MBA application",
        key_facts=(
            "Applying to the Stanford GSB Class of 2028",
            "Took Professor Allen's Applied Econometrics course in 2022",
            "Recommendation deadline is September 8th",
            "Happy to share updated resume and program details",
        ),
        tone="formal",
        reference_email="""Subject: Recommendation Letter — Stanford GSB Application

Dear Professor Allen,

I hope you are doing well. I took your Applied Econometrics course in 2022 — it remains one of the most memorable classes from my undergraduate years.

I am writing to ask if you would be willing to write me a recommendation for my Stanford GSB application, Class of 2028. The letter is due by September 8th.

If you are open to it, I would be glad to send over my updated resume, details on the program, and a short note on the themes I am highlighting — whatever would be most useful to you.

Thank you for considering this request.

Warm regards,
[Your Name]""",
    ),
    Scenario(
        id="S10-casual-vendor-renewal",
        intent="Ask a SaaS vendor for a discount on our upcoming renewal",
        key_facts=(
            "Current contract renews May 30th at $48k per year",
            "We have been customers for three years and referred two companies",
            "Looking for a 15% discount or additional seats at the same price",
            "Happy to sign a two-year renewal to lock in the rate",
        ),
        tone="casual",
        reference_email="""Subject: Quick chat about our May renewal?

Hey [Rep],

Our renewal is coming up on May 30th at $48k a year, and I wanted to kick off the conversation early rather than wait until the wire.

We've been with you for three years now and sent two other companies your way, so I'm hoping we can land on a good number for year four. Ideally a 15% discount, or keep the price flat and throw in some extra seats.

Happy to sign a two-year renewal to lock the rate in if that helps on your side.

Let me know — happy to hop on a call this week.

Thanks,
[Your Name]""",
    ),
]


assert len(SCENARIOS) == 10
