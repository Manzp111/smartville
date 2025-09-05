```mermaid
sequenceDiagram
    autonumber
    participant Visitor as System Visitor
    participant GPS as GPS Service
    participant Resident
    participant Guest as Guest of Resident
    participant System
    participant Leader as Village Leader
    participant WebSocket as Notification Service

    %% Visitor enters SmartVillage
    Visitor->>System: Open landing page
    System-->>Visitor: Show options (View Public Info / Register / Browse Events)

    %% Visitor browsing
    Visitor->>System: View village info by selection
    System-->>Visitor: Show public village info
    Visitor->>GPS: Share current location
    GPS-->>System: Send village coordinates
    System-->>Visitor: Show nearby village info/events

    %% Visitor registers as Resident
    Visitor->>System: Submit registration info
    System-->>Visitor: Registration confirmation
    System->>Resident: Create Resident account
    System->>Leader: Notify new Resident
    WebSocket-->>Resident: Push registration success

    %% Resident adds Guests
    Resident->>System: Add Guest(s)
    System-->>Resident: Guest(s) added confirmation
    System-->>Guest: Send guest info
    WebSocket-->>Guest: Push guest notification

    %% Resident submits Event/Conference/Volunteering/Meeting
    Resident->>System: Submit Event/Activity
    System-->>System: Store as Pending
    System->>Leader: Notify pending Event/Activity
    Leader->>System: Approve/Reject Event/Activity
    System-->>Resident: Event/Activity status
    System-->>Guest: Update Event/Activity feed
    System-->>Visitor: Update Event/Activity feed
    WebSocket-->>Resident: Push event approval/updates
    WebSocket-->>Guest: Push event updates

    %% Resident submits Service Request
    Resident->>System: Submit Service Request
    System-->>System: Store request as Pending
    System->>Leader: Notify pending Service Request
    Leader->>System: Approve/Assign Request + Set Priority
    System-->>Resident: Service request status
    WebSocket-->>Resident: Push request update

    %% Optional: Event recommendations
    System-->>Resident: Show recommended events (location & interest based)
