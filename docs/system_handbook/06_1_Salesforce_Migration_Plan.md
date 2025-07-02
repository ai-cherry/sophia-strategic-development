# Deep Dive: Salesforce to Intercom/HubSpot Migration Plan

> **Version:** 1.0  
> **Status:** Planning  
> **Parent:** [SOPHIA_AI_SYSTEM_HANDBOOK.md](./00_SOPHIA_AI_SYSTEM_HANDBOOK.md)

---

## 1. Executive Summary

This document outlines the strategic plan for migrating our core CRM and customer communication functionalities from Salesforce to a modern, integrated stack consisting of **HubSpot (CRM)** and **Intercom (Customer Messaging)**.

This migration is not a simple "lift and shift." It is an opportunity to re-architect our customer data flow around a more agile, AI-native, and developer-friendly ecosystem. We will leverage our **N8N orchestration engine** to manage the entire migration process, ensuring data integrity, zero downtime for sales and support teams, and a seamless transition.

## 2. Rationale for Migration

-   **High Cost & Complexity:** Salesforce's licensing costs and complex, proprietary development environment (Apex, Visualforce) create significant overhead.
-   **Poor Developer Experience:** The modern data stack (HubSpot, Intercom) offers superior, API-first developer experiences, enabling faster and more flexible integrations.
-   **Limited AI Integration:** While Salesforce has Einstein, HubSpot and Intercom are built with more open and flexible AI integration points that align better with the Sophia AI platform.
-   **Strategic Alignment:** HubSpot and Intercom are better suited for the high-velocity, SMB-focused sales motion that Pay Ready is targeting.

## 3. The Migration Strategy: An N8N-Orchestrated Approach

We will use N8N as the central orchestrator for a phased, gradual migration. This approach mitigates risk and allows us to build and validate the new system in parallel before decommissioning the old one.

```mermaid
graph TD
    subgraph Phase 1: Dual-Write & Sync
        A[Salesforce]
        B[N8N Migration Workflow]
        C[HubSpot]
        D[Intercom]
        
        A -- Real-time via Outbound Messages --> B
        B -- Writes to --> C
        B -- Writes to --> D
    end

    subgraph Phase 2: Read from New System
        E[Sophia AI Platform]
        E -- Reads from --> C
        E -- Reads from --> D
    end

    subgraph Phase 3: Write to New System
        F[Sophia AI Platform]
        G[N8N Write-Back Workflow]
        F -- Writes to --> G
        G -- Writes back to --> A
        G -- Writes to --> C
        G -- Writes to --> D
    end
    
    subgraph Phase 4: Decommission Salesforce
        H[Salesforce (Read-Only)]
        I[Final Data Cutover]
        H -.-> I
    end
    
    style B fill:#7E57C2,stroke:#FFF,stroke-width:2px,color:#FFF
    style G fill:#7E57C2,stroke:#FFF,stroke-width:2px,color:#FFF
```

## 4. Phased Implementation Plan

### **Phase 1: Dual-Write & Synchronization**

-   **Goal:** Establish a one-way data flow from Salesforce to HubSpot/Intercom, ensuring the new systems are always an up-to-date mirror of the old one.
-   **Actions:**
    1.  **Build N8N "Sync" Workflow:** Create a robust N8N workflow that listens for changes in Salesforce (using Outbound Messages or scheduled polling).
    2.  **Map Data Models:** The workflow will be responsible for mapping Salesforce objects (Accounts, Contacts, Opportunities, Leads) to their corresponding objects in HubSpot (Companies, Contacts, Deals) and Intercom (Users, Companies).
    3.  **Deploy & Monitor:** Activate the workflow and monitor it closely to ensure data is flowing accurately and reliably. The sales team continues to work exclusively in Salesforce.

### **Phase 2: Shift Reads to New Systems**

-   **Goal:** Modify all internal Sophia AI services and dashboards to read data *from* HubSpot and Intercom instead of Salesforce.
-   **Actions:**
    1.  **Update Data Models:** Refactor our internal application code to use the HubSpot and Intercom data models.
    2.  **Switch Read Endpoints:** Point all data-reading functionalities (e.g., generating sales reports, populating dashboards) to the new HubSpot/Intercom APIs.
    3.  **Validation:** The sales team still writes to Salesforce, but all our internal reporting and intelligence are now powered by the new stack. This allows us to validate the data integrity of the new system in a read-only context.

### **Phase 3: Shift Writes to New Systems**

-   **Goal:** Enable writing data back to the new systems, with N8N ensuring both old and new systems remain in sync during the transition.
-   **Actions:**
    1.  **Build N8N "Write-Back" Workflow:** Create a new N8N workflow that our platform can call.
    2.  **Implement Dual-Write Logic:** When our platform needs to create or update a record (e.g., AI logs a call summary), it calls this N8N workflow. The workflow then writes the data to **both** HubSpot/Intercom **and** back to Salesforce.
    3.  **Pilot Program:** A small, dedicated group of "power users" from the sales team begins using a new interface powered by Sophia AI to manage their data, which triggers this dual-write process.

### **Phase 4: Final Cutover & Decommission**

-   **Goal:** Move all users to the new system and turn off Salesforce for good.
-   **Actions:**
    1.  **Full Team Onboarding:** Train and migrate the entire sales and support teams to use the new HubSpot/Intercom interfaces and the Sophia AI platform.
    2.  **Make Salesforce Read-Only:** Disable all write access to Salesforce, effectively freezing it.
    3.  **Final Data Reconciliation:** Run a final, one-time N8N workflow to perform a comprehensive data reconciliation, ensuring any last-minute changes are perfectly synced to the new systems.
    4.  **Decommission:** Once the new system has been stable for a set period, we can terminate our Salesforce contract.

## 5. Strengths of this Plan

-   **Zero Downtime:** At no point during the migration is the sales or support team without a functional CRM.
-   **Risk Mitigation:** The phased approach allows us to validate each step before proceeding to the next, dramatically reducing the risk of data loss or corruption.
-   **Leverages Existing Strengths:** We use our core N8N orchestration engine to do the heavy lifting, avoiding the need for expensive, specialized ETL tools.
-   **AI-Native from Day One:** The new system is designed from the ground up to be integrated with Sophia AI, unlocking powerful automation capabilities that were not possible with Salesforce.
