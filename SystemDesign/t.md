```mermaid 
flowchart LR
    %% Central Smart Village System
    S((Smart Village<br/>Platform))

    %% External Entities - grouped
    subgraph LeftActors[ ]
        direction TB
        R[Resident]
        V[Visitor]
    end

    subgraph RightActors[ ]
        direction TB
        L[Village Leader]
        SMS[SMS Service]
    end

    %% Inputs (to system)
    R -->|" Login Credentials"| S
    R -->|" Complaint Submission"| S
    R -->|" Event Posting"| S
    R -->|" Visitor Registration"| S

    V -->|" Village Selection(dropdown/GPS)"| S
    V -->|" Public Info Query"| S
    L -->|" Admin Login"| S
    L -->|" Official Alerts"| S
    L -->|" Complaint Updates"| S

    SMS -->|" SMS Status Report"| S

    %% Outputs (from system)
    S -->|" Auth Result"| R
    S -->|" Complaint Status"| R
    S -->|" Notifications"| R

    S -->|" Village Information"| V

    S -->|" Admin Dashboard"| L
    S -->|" Alert Confirmation"| L

    S -->|" SMS Messages"| SMS

    %% Styling for nodes
    style S fill:#4A90E2,stroke:#2E5A87,stroke-width:3px,color:#fff
    style R fill:#7ED321,stroke:#5BA517,stroke-width:2px,color:#fff
    style V fill:#F5A623,stroke:#D4861A,stroke-width:2px,color:#fff
    style L fill:#D0021B,stroke:#A0021B,stroke-width:2px,color:#fff
    style SMS fill:#9013FE,stroke:#6A0DAD,stroke-width:2px,color:#fff
