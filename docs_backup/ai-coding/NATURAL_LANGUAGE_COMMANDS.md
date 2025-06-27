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
@docker compose up all services

@docker restart the database container

@docker scale api service to 3 instances

@docker update service with new image
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
| Fix bug | `@sophia debug [error]` |
| Analyze quality | `@codacy analyze` |
| Remember decision | `@memory store [info]` |
| Create PR | `@github create PR [title]` |
| Build container | `@docker build` |
| Explain concept | `@sophia explain [topic]` |
| Find past solution | `@memory search [problem]` |
| Security check | `@codacy security scan` |
| Deploy | `@docker deploy to [env]` |

---

**Remember:** Natural language is powerful - the more context you provide, the better the results. Don't be afraid to have a conversation with Sophia!
