# Amazon Repricing Tool System Architecture

# Amazon Repricing Tool - System Architecture Design

## 1. SYSTEM OVERVIEW

### 1.1 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐   │
│  │   Web App      │  │   Mobile App    │  │   Admin Panel    │   │
│  │  (Next.js)     │  │   (Optional)    │  │   (Next.js)      │   │
│  └────────┬───────┘  └────────┬────────┘  └────────┬─────────┘   │
└───────────┴──────────────────┴─────────────────────┴──────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         API GATEWAY LAYER                           │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │  API Gateway (NestJS)                                       │  │
│  │  • Rate Limiting  • Auth Middleware  • Request Validation   │  │
│  │  • CORS          • Logging          • Error Handling        │  │
│  └─────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      APPLICATION SERVICES LAYER                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │     Auth     │  │   Product    │  │    Repricing         │    │
│  │   Service    │  │   Service    │  │     Engine           │    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │   Amazon     │  │   Analytics  │  │   Notification       │    │
│  │ Integration  │  │   Service    │  │     Service          │    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │    Price     │  │   Settings   │  │      Audit           │    │
│  │   Monitor    │  │   Service    │  │     Service          │    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌─────────────────────────┐    ┌─────────────────────────┐
│   DOMAIN LAYER          │    │   INFRASTRUCTURE LAYER  │
│  • Business Entities    │    │  • Repositories         │
│  • Domain Services      │    │  • External APIs        │
│  • Business Rules       │    │  • Database Access      │
│  • Value Objects        │    │  • Cache Management     │
└─────────────────────────┘    └─────────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    ▼                      ▼                      ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│    PostgreSQL        │  │      Redis           │  │   Amazon SP-API      │
│   (Primary DB)       │  │  (Cache & Queue)     │  │  (External Service)  │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘
```

### 1.2 Architectural Pattern

**Clean Architecture (Hexagonal Architecture) with Domain-Driven Design (DDD)**

**Justification:**
- **Separation of Concerns**: Clean separation between business logic and infrastructure
- **Testability**: Business logic can be tested independently of frameworks
- **Flexibility**: Easy to swap out infrastructure components (database, external APIs)
- **Maintainability**: Clear boundaries between layers make the codebase easier to understand
- **Scalability**: Services can be scaled independently based on load
- **Domain Focus**: DDD ensures the architecture reflects the business domain accurately

## 2. COMPONENT BREAKDOWN

### 2.1 Core Application Services

#### Authentication Service
**Responsibilities:**
- User registration and validation
- Login/logout management
- JWT token generation and validation
- Password hashing and verification
- MFA implementation
- Session management
- Password reset flow

**Interfaces:**
```typescript
interface IAuthService {
  register(dto: RegisterDto): Promise<User>
  login(credentials: LoginDto): Promise<AuthResponse>
  validateToken(token: string): Promise<TokenPayload>
  refreshToken(refreshToken: string): Promise<AuthResponse>
  resetPassword(token: string, newPassword: string): Promise<void>
  enableMFA(userId: string): Promise<MFASecret>
}
```

#### Product Service
**Responsibilities:**
- Product CRUD operations
- Bulk import/export functionality
- Product search and filtering
- Category management
- SKU/ASIN mapping
- Product synchronization with Amazon

**Interfaces:**
```typescript
interface IProductService {
  importFromAmazon(accountId: string): Promise<Product[]>
  createProduct(dto: CreateProductDto): Promise<Product>
  updateProduct(id: string, dto: UpdateProductDto): Promise<Product>
  deleteProduct(id: string): Promise<void>
  bulkImport(file: Buffer): Promise<ImportResult>
  searchProducts(query: SearchQuery): Promise<PaginatedResult<Product>>
}
```

#### Repricing Engine
**Responsibilities:**
- Strategy pattern implementation for pricing algorithms
- Rule evaluation and prioritization
- Price calculation with boundaries
- Bulk repricing operations
- Preview mode calculations
- Manual override management

**Interfaces:**
```typescript
interface IRepricingEngine {
  calculatePrice(product: Product, strategy: RepricingStrategy): Promise<number>
  applyRules(products: Product[]): Promise<RepricingResult[]>
  previewChanges(products: Product[]): Promise<PreviewResult[]>
  executeRepricing(productIds: string[]): Promise<void>
  createRule(dto: CreateRuleDto): Promise<RepricingRule>
}
```

#### Amazon Integration Service
**Responsibilities:**
- SP-API client wrapper
- OAuth flow management
- Rate limiting and throttling
- Error handling and retries
- Marketplace management
- Credential encryption/decryption

**Interfaces:**
```typescript
interface IAmazonService {
  authorizeAccount(authCode: string): Promise<AmazonAccount>
  getProducts(accountId: string): Promise<AmazonProduct[]>
  updatePrice(sku: string, price: number): Promise<void>
  getCompetitorPrices(asin: string): Promise<CompetitorPrice[]>
  getBuyBoxPrice(asin: string): Promise<number>
}
```

#### Price Monitor Service
**Responsibilities:**
- Scheduled price polling
- Competitor tracking
- Price change detection
- Alert triggering
- Historical data management
- Buy Box monitoring

**Interfaces:**
```typescript
interface IPriceMonitorService {
  scheduleMonitoring(productId: string, interval: number): Promise<void>
  checkPrices(productIds: string[]): Promise<PriceCheckResult[]>
  trackCompetitor(competitorId: string): Promise<void>
  getPriceHistory(productId: string, range: DateRange): Promise<PriceHistory[]>
}
```

#### Analytics Service
**Responsibilities:**
- Metrics calculation
- Report generation
- Data aggregation
- Chart data preparation
- Export functionality
- Dashboard data compilation

**Interfaces:**
```typescript
interface IAnalyticsService {
  getDashboardMetrics(userId: string): Promise<DashboardData>
  generateReport(type: ReportType, params: ReportParams): Promise<Report>
  calculateProfitability(dateRange: DateRange): Promise<ProfitData>
  getBuyBoxWinRate(productIds: string[]): Promise<WinRateData>
  exportData(format: ExportFormat): Promise<Buffer>
}
```

#### Notification Service
**Responsibilities:**
- Email delivery
- In-app notification management
- Webhook dispatching
- Template management
- Notification preferences
- Delivery tracking

**Interfaces:**
```typescript
interface INotificationService {
  sendEmail(to: string, template: EmailTemplate, data: any): Promise<void>
  createNotification(userId: string, notification: NotificationDto): Promise<void>
  triggerWebhook(url: string, event: WebhookEvent): Promise<void>
  updatePreferences(userId: string, preferences: NotificationPrefs): Promise<void>
}
```

### 2.2 Shared Components/Utilities

#### Common Utilities
- **Logger**: Centralized logging with correlation IDs
- **Validator**: Input validation utilities
- **Encryption**: Cryptographic operations
- **DateUtils**: Date/time manipulation
- **ErrorHandler**: Global error handling
- **Mapper**: DTO to Entity mapping

#### Middleware Components
- **AuthMiddleware**: JWT validation
- **RateLimitMiddleware**: Request throttling
- **LoggingMiddleware**: Request/response logging
- **ValidationMiddleware**: Input validation
- **ErrorMiddleware**: Error formatting

## 3. TECHNOLOGY STACK

### 3.1 Backend Framework
**NestJS with TypeScript**

**Rationale:**
- Enterprise-grade Node.js framework with excellent TypeScript support
- Built-in dependency injection for clean architecture
- Modular architecture aligns with our component design
- Extensive ecosystem and community support
- Built-in support for microservices if needed for scaling
- Excellent testing capabilities

### 3.2 Database
**Primary: PostgreSQL 15+**

**Rationale:**
- ACID compliance for financial data integrity
- Excellent performance with proper indexing
- JSON support for flexible schema portions
- Strong consistency for pricing operations
- Mature ecosystem and tooling
- Row-level security capabilities

**Secondary: Redis 7+**

**Rationale:**
- High-performance caching layer
- Session storage
- Queue management (BullMQ)
- Real-time data for dashboards
- Pub/Sub for real-time notifications

### 3.3 API Technology
**REST with OpenAPI/Swagger**

**Rationale:**
- Well-understood by developers
- Excellent tooling support
- Easy to document with Swagger
- Stateless nature suits our architecture
- GraphQL considered but REST is simpler for this use case

**WebSocket for Real-time Features:**
- Price update notifications
- Dashboard live updates
- In-app notifications

### 3.4 Authentication/Authorization
**JWT with Refresh Tokens**

**Implementation:**
- Access tokens (15 min expiry)
- Refresh tokens (7 days expiry)
- Role-based access control (RBAC)
- Optional MFA with TOTP

### 3.5 Caching Strategy
**Multi-layer Caching:**

1. **Application Cache (Redis)**
   - User sessions
   - Frequently accessed products
   - Dashboard metrics (5 min TTL)
   - API rate limit counters

2. **Database Query Cache**
   - Query result caching
   - Prepared statement caching

3. **CDN Cache (Frontend)**
   - Static assets
   - API responses where appropriate

### 3.6 Message Queue
**BullMQ (Redis-based)**

**Use Cases:**
- Background price updates
- Scheduled monitoring tasks
- Email delivery
- Report generation
- Bulk import/export operations

## 4. DATA ARCHITECTURE

### 4.1 Database Schema Design

```sql
-- Core User Management
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Amazon Account Integration
CREATE TABLE amazon_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    marketplace_id VARCHAR(50) NOT NULL,
    seller_id VARCHAR(100) NOT NULL,
    credentials_encrypted TEXT,
    oauth_token TEXT,
    refresh_token TEXT,
    token_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, marketplace_id, seller_id)
);

-- Product Management
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    amazon_account_id UUID REFERENCES amazon_accounts(id) ON DELETE CASCADE,
    asin VARCHAR(20) NOT NULL,
    sku VARCHAR(100) NOT NULL,
    title TEXT NOT NULL,
    current_price DECIMAL(10,2) NOT NULL,
    cost DECIMAL(10,2),
    min_price DECIMAL(10,2),
    max_price DECIMAL(10,2),
    repricing_enabled BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_account_sku (amazon_account_id, sku),
    INDEX idx_asin (asin)
);

-- Repricing Rules
CREATE TABLE repricing_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    strategy_type VARCHAR(50) NOT NULL,
    parameters JSONB NOT NULL,
    priority INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,