# 💬 **Natural Language Commands Reference**

> **Complete guide to conversing with Sophia AI's MCP servers using natural language.** No more memorizing syntax - just describe what you want!

## **🎯 Command Patterns**

### **Basic Pattern**
```
@[server] [action] [target] [options]
```

### **Examples**
```bash
@sophia generate a user authentication system
@codacy analyze this file for security issues  
@memory remember we use PostgreSQL for main database
@github create PR for authentication feature
```

**Note:** All UI generation requests go through the unified chat interface. Simply type your request naturally without any @ prefix:
```bash
"Create a dashboard component with glassmorphism"
"Build a responsive navigation bar"
"Generate a data table with sorting"
```

## **📚 Sophia AI Intelligence Commands**

### **Code Generation**

#### **Complete Features**
```bash
@sophia create a complete user management system with:
- User registration and login
- JWT authentication
- Password reset via email
- Role-based permissions
- Profile management

@sophia build a real-time chat application using:
- WebSockets for messaging
- Redis for pub/sub
- PostgreSQL for message history
- React for frontend
```

#### **Specific Components**
```bash
# API Endpoints
@sophia generate REST API endpoints for product management with CRUD operations

# Database Models
@sophia create SQLAlchemy models for an e-commerce system

# Frontend Components
@sophia build a React dashboard component with charts and metrics

# Microservices
@sophia design a microservice for payment processing with Stripe
```

#### **Test Generation**
```bash
# Unit Tests
@sophia write comprehensive pytest tests for the UserService class

# Integration Tests  
@sophia create integration tests for the authentication API

# E2E Tests
@sophia generate Cypress tests for the user registration flow

# Performance Tests
@sophia create load tests for the API using Locust
```

### **Code Analysis & Improvement**

#### **Architecture Review**
```bash
@sophia analyze the architecture of this module and suggest improvements

@sophia is this code following SOLID principles?

@sophia review this class for design patterns and best practices

@sophia how can we make this service more scalable?
```

#### **Performance Optimization**
```bash
@sophia optimize this function for better performance

@sophia identify bottlenecks in this code

@sophia suggest caching strategies for this API

@sophia how can we reduce the memory usage of this process?
```

#### **Security Analysis**
```bash
@sophia check this code for security vulnerabilities

@sophia review this authentication implementation for security issues

@sophia suggest security improvements for this API

@sophia analyze SQL injection risks in this code
```

### **Debugging & Problem Solving**

#### **Error Debugging**
```bash
@sophia help me fix this error: TypeError: cannot read property 'id' of undefined

@sophia debug: API returns 500 error when processing large files

@sophia why is this async function not waiting for the promise?

@sophia trace the execution flow that leads to this error
```

#### **Concept Explanation**
```bash
@sophia explain how JWT authentication works

@sophia what's the difference between REST and GraphQL?

@sophia how does Python's async/await work under the hood?

@sophia explain the benefits of microservices architecture
```

## **🔍 Codacy Commands**

### **Code Quality Analysis**
```bash
# Analyze current file
@codacy analyze this file

# Analyze entire project
@codacy scan the whole project for issues

# Specific checks
@codacy check for code duplication
@codacy find security vulnerabilities
@codacy analyze code complexity
@codacy check test coverage
```

### **Automated Fixes**
```bash
@codacy fix the style issues in this file

@codacy apply security patches

@codacy refactor complex methods

@codacy remove code duplication
```

## **🧠 AI Memory Commands**

### **Storing Information**
```bash
# Architecture decisions
@memory remember: We chose PostgreSQL over MongoDB because we need ACID compliance

# Technical choices
@memory store: Using Redis for session management with 15-minute TTL

# Bug solutions
@memory save: Fixed timeout issue by implementing connection pooling

# Code patterns
@memory record: Always use dependency injection for service classes
```

### **Retrieving Information**
```bash
# Search by topic
@memory what database did we choose?

# Search by problem
@memory how did we fix the authentication timeout?

# Search by pattern
@memory what's our standard error handling pattern?

# Recent decisions
@memory show recent architecture decisions
```

## **🐙 GitHub Commands**

### **Repository Operations**
```bash
# Create pull request
@github create PR titled "Add user authentication feature"

# Create issue
@github open issue: "Performance degradation in search API"

# Branch operations
@github create feature branch for payment integration

# Code review
@github request review from senior developers
```

### **Workflow Management**
```bash
@github run CI/CD pipeline

@github check workflow status

@github deploy to staging environment

@github tag release v2.1.0
```

## **🐳 Docker Commands**

### **Container Management**
```bash
# Build and run
@docker build and run the application

# Development environment
@docker start development environment with hot reload

# Production deployment
@docker build optimized production image

# Debugging
@docker show logs for the api container
```

### **Compose Operations**
```bash
@docker check service status on Lambda Labs

@docker restart the database container

@docker scale api service to 3 instances

@docker update service with new image
```

## **🎨 UI Generation Through Unified Chat**

### **Component Creation (via Unified Chat)**

#### **Dashboard Components**
```bash
# Executive dashboard
"Create an executive dashboard with KPI cards and glassmorphism styling"

# Analytics dashboard
"Build a dashboard showing revenue, user growth, and performance metrics"

# Real-time dashboard
"Generate a real-time monitoring dashboard with live charts"

# Mobile dashboard
"Design a responsive mobile-friendly dashboard"
```

#### **Form Components**
```bash
# Contact form
"Create a contact form with email validation and submit handling"

# Multi-step form
"Build a multi-step registration form with progress indicator"

# Dynamic form
"Generate a dynamic form builder with drag-and-drop fields"

# Login form
"Design a modern login form with social auth buttons"
```

#### **Data Display**
```bash
# Data table
"Create a data table with sorting, filtering, and pagination"

# Card grid
"Build a product card grid with hover effects"

# List view
"Generate a user list with avatars and action buttons"

# Timeline
"Design a vertical timeline component for events"
```

#### **Navigation**
```bash
# Header
"Create a responsive header with dropdown navigation"

# Sidebar
"Build a collapsible sidebar with nested menu items"

# Breadcrumbs
"Generate a breadcrumb component with icons"

# Tab navigation
"Design a tab component with animated transitions"
```

### **Style-Specific Requests (via Unified Chat)**

#### **Modern Styles**
```bash
# Glassmorphism
"Create a glassmorphism card component with blur effect"

# Neumorphism
"Build neumorphic buttons with pressed states"

# Gradient
"Generate a gradient hero section with animated background"

# Minimal
"Design a minimal pricing card with clean typography"
```

#### **Theme Variations**
```bash
# Dark theme
"Create a dark theme dashboard with neon accents"

# Light theme
"Build a light theme form with soft shadows"

# High contrast
"Generate an accessible high-contrast data table"

# Custom brand
"Design components matching our brand colors #FF6B6B and #4ECDC4"
```

### **Framework-Specific Generation (via Unified Chat)**

```bash
# React + TypeScript
"Create a React TypeScript component for user profile management"

# Next.js
"Build a Next.js layout component with SSR support"

# Tailwind CSS
"Generate a component using only Tailwind CSS classes"

# Material-UI
"Design a component using Material-UI v5 components"
```

### **Advanced UI Features (via Unified Chat)**

```bash
# Animations
"Create a card with smooth hover animations and transitions"

# Interactive charts
"Build a dashboard with interactive Chart.js visualizations"

# Drag and drop
"Generate a kanban board with drag-and-drop functionality"

# Real-time updates
"Design a component with WebSocket real-time data updates"
```

## **🔄 Workflow Combinations**

### **Feature Development Flow**
```bash
# 1. Start with idea
@sophia help me design a notification system

# 2. Generate implementation
@sophia create notification service with email and SMS support

# 3. Quality check
@codacy analyze the notification service code

# 4. Store decisions
@memory remember: Using Twilio for SMS and SendGrid for email

# 5. Create tests
@sophia generate tests for NotificationService

# 6. Version control
@github create feature/notifications branch and PR
```

### **Bug Fix Flow**
```bash
# 1. Understand the issue
@sophia explain this error: ConnectionRefusedError

# 2. Check history
@memory have we seen connection errors before?

# 3. Get solution
@sophia how to implement retry logic with exponential backoff

# 4. Verify fix
@codacy check if the retry logic is implemented correctly

# 5. Document
@memory save: Added retry logic to handle transient connection failures
```

### **Code Review Flow**
```bash
# 1. Get overview
@sophia summarize the changes in PR #123

# 2. Security check
@codacy scan PR for security vulnerabilities

# 3. Architecture review
@sophia does this follow our microservices patterns?

# 4. Performance check
@sophia analyze performance impact of these changes

# 5. Suggest improvements
@sophia suggest refactoring for better maintainability
```

### **UI Development Flow (via Unified Chat)**
```bash
# 1. Design the component
"Create a user profile card with avatar and social links"

# 2. Review accessibility  
"Ensure the component meets WCAG 2.1 standards"

# 3. Check code quality
"Analyze the generated component code for quality issues"

# 4. Save design decision
"Remember: Using glassmorphism style for all profile cards"

# 5. Create tests
"Generate React tests for the ProfileCard component"

# 6. Integrate
"Show me how to integrate this component into our dashboard"
```

## **💡 Pro Tips**

### **Be Specific**
```bash
# ❌ Vague
@sophia create a function

# ✅ Specific
@sophia create an async Python function that fetches user data from PostgreSQL, 
caches it in Redis for 5 minutes, and includes error handling
```

### **Provide Context**
```bash
# ❌ No context
@sophia fix this error

# ✅ With context
@sophia fix this error in our FastAPI application: 
"RuntimeError: Event loop is closed" when running async tests
```

### **Chain Commands**
```bash
# Generate → Analyze → Improve
@sophia create user authentication endpoint &&
@codacy analyze security &&
@sophia apply security best practices
```

### **Use Memory Effectively**
```bash
# Before making decisions
@memory what authentication method did we use in other services?

# After implementing
@memory remember: Implemented OAuth2 with JWT for user service
```

## **🎨 Advanced Patterns**

### **Conditional Commands**
```bash
@sophia if this is a public API, add rate limiting

@codacy only fix critical security issues

@memory search for similar issues in the last month
```

### **Batch Operations**
```bash
@sophia generate CRUD endpoints for all models in models.py

@codacy analyze all files changed in the last commit

@docker restart all services except database
```

### **Interactive Flows**
```bash
@sophia walk me through implementing a payment system step by step

@sophia explain each line of this complex algorithm

@codacy show me issues one by one with explanations
```

## **🚀 Quick Reference Card**

| Need | Command |
|------|---------|
| Generate code | `@sophia create [description]` |
| Generate UI | Type naturally: `"Create [component]"` |
| Fix bug | `@sophia debug [error]` |
| Analyze quality | `@codacy analyze` |
| Remember decision | `@memory store [info]` |
| Create PR | `@github create PR [title]` |
| Build container | `@docker build` |
| Design interface | Type naturally: `"Design [UI element]"` |
| Explain concept | `@sophia explain [topic]` |
| Find past solution | `@memory search [problem]` |
| Security check | `@codacy security scan` |
| Deploy | `@docker deploy to [env]` |

---

**Remember:** Natural language is powerful - the more context you provide, the better the results. Don't be afraid to have a conversation with Sophia!
