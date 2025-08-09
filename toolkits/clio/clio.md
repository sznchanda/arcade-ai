# Clio API Documentation - Comprehensive Reference

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Rate Limits](#rate-limits)
4. [Pagination](#pagination)
5. [Field Selection](#field-selection)
6. [Clio Manage API (v4)](#clio-manage-api-v4)
7. [Clio Grow API (v2)](#clio-grow-api-v2)
8. [Clio Payments API](#clio-payments-api)
9. [Personal Injury API](#personal-injury-api)
10. [Webhooks](#webhooks)
11. [SDKs and Integration](#sdks-and-integration)

## Overview

The Clio API provides programmatic access to Clio's comprehensive legal practice management platform. This documentation covers multiple API versions and specialized endpoints for different Clio products.

### Base URLs
- **Clio Manage API v4**: `https://app.clio.com/api/v4`
- **Clio Grow API v2**: 
  - US: `https://grow.clio.com/api/v2`
  - EU: `https://eu.grow.clio.com/api/v2`
  - AU: `https://au.grow.clio.com/api/v2`

### Regional Availability
The API is available in three distinct data regions:
- **United States**: app.clio.com, grow.clio.com
- **European Union**: eu.app.clio.com, eu.grow.clio.com
- **Australia**: au.app.clio.com, au.grow.clio.com

## Authentication

### OAuth 2.0 Authorization Flow

Clio implements OAuth 2.0 for secure authentication. All API requests must include a valid access token in the Authorization header:

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

#### Step 1: Get Authorization Code

Redirect users to Clio's authorization endpoint:

```
https://app.clio.com/oauth/authorize?response_type=code&client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&state=RANDOM_STATE
```

**Parameters:**
- `client_id`: Your application key (required)
- `response_type`: Set to "code" (required)
- `redirect_uri`: Your registered redirect URL (required)
- `state`: Opaque value for security (recommended)
- `redirect_on_decline`: When "true", redirects on permission denial (optional)

**Grant Approved Response:**
```
http://yourapp.com/callback?code=AUTHORIZATION_CODE&state=RANDOM_STATE
```

**Grant Declined Response:**
```
http://yourapp.com/callback?error=access_denied&state=RANDOM_STATE
```

#### Step 2: Exchange Code for Access Token

Make a POST request to exchange the authorization code:

```bash
curl -X POST "https://app.clio.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=authorization_code" \
  -d "code=AUTHORIZATION_CODE" \
  -d "redirect_uri=YOUR_REDIRECT_URI"
```

**Response:**
```json
{
  "token_type": "bearer",
  "access_token": "WjR8HL...dU2ul",
  "expires_in": 604800,
  "refresh_token": "5A0Dd...Gvx7e"
}
```

#### Token Refresh

Use the refresh token to obtain a new access token:

```bash
curl -X POST "https://app.clio.com/oauth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "grant_type=refresh_token" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

#### Token Deauthorization

Revoke an access token:

```bash
curl -X POST "https://app.clio.com/oauth/deauthorize" \
  -H "Authorization: Bearer ACCESS_TOKEN" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "token=ACCESS_TOKEN"
```

### Mobile and Desktop Applications

For desktop/mobile apps:
- Use web views for authorization flow
- Use `https://app.clio.com/oauth/approval` as redirect_uri
- Extract authorization code from URL or page title
- Handle platform-specific redirect interception

## Rate Limits

### Default Rate Limits
- **Standard**: 50 requests per minute during peak hours
- **Off-peak**: Higher limits (varies by region)
- **Maximum**: No custom rate limit increases available

### Peak Hours
- **US/CA**: 04:00-19:00 Pacific Time, Monday-Friday  
- **EU**: 07:00-22:00 GMT, Monday-Friday
- **AU**: 06:00-21:00 AET, Monday-Friday

### Rate Limit Headers
Every API response includes:
- `X-RateLimit-Limit`: Maximum requests per 60-second window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Unix timestamp when window resets

### Rate Limit Exceeded (429 Response)
When exceeded, responses include:
- `Retry-After`: Seconds to wait before retrying

## Pagination

Index actions are limited to 200 results per request. Clio supports two pagination approaches:

### Limited Offset Pagination
- **Use case**: Parallelizable requests, custom sort orders
- **Limit**: 10,000 total records (50 pages)
- **Parameters**: Include `offset` parameter
- **Sorting**: Custom sort orders supported per endpoint

```bash
curl "https://app.clio.com/api/v4/activities?fields=id,quantity,price,total&offset=10"
```

### Unlimited Cursor Pagination
- **Use case**: Unlimited records, sequential processing
- **Requirement**: `order=id(asc)` parameter, no `offset`
- **Limitation**: Serial requests only (no parallelization)

```bash
curl "https://app.clio.com/api/v4/activities?fields=id,quantity,price,total&order=id(asc)"
```

### Pagination Metadata
Responses include pagination information:

```json
{
  "data": { ... },
  "meta": {
    "paging": {
      "previous": "https://app.clio.com/api/v4/contacts?fields=...",
      "next": "https://app.clio.com/api/v4/contacts?fields=..."
    }
  }
}
```

## Field Selection

### Basic Field Selection
Use the `fields` parameter to specify desired fields:

```bash
https://app.clio.com/api/v4/activities?fields=id,etag,type
```

### Nested Resources
Request fields for nested resources using curly brackets:

```bash
https://app.clio.com/api/v4/activities?fields=id,etag,type,matter{id,description}
```

**Limitations:**
- Second-level nested resources return default fields only
- Deep nesting beyond two levels not supported

### POST/PATCH Field Selection
Include `fields` parameter in create/update requests:

```bash
curl -X POST "https://app.clio.com/api/v4/activities?fields=id,etag,total" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"data": {"date": "2022-09-26", "quantity": 7200, "price": 200, "type": "TimeEntry"}}'
```

## Clio Manage API (v4)

### Core Resources

#### Activities
Time entries and expense tracking:
- `GET /activities` - List all activities
- `POST /activities` - Create new activity
- `GET /activities/{id}` - Get single activity
- `PATCH /activities/{id}` - Update activity
- `DELETE /activities/{id}` - Delete activity

#### Activity Descriptions
Standardized activity descriptions:
- `GET /activity_descriptions` - List descriptions
- `POST /activity_descriptions` - Create description
- `GET /activity_descriptions/{id}` - Get single description
- `PATCH /activity_descriptions/{id}` - Update description
- `DELETE /activity_descriptions/{id}` - Delete description

#### Activity Rates
Billing rates for activities:
- `GET /activity_rates` - List all rates
- `POST /activity_rates` - Create new rate
- `GET /activity_rates/{id}` - Get single rate
- `PATCH /activity_rates/{id}` - Update rate
- `DELETE /activity_rates/{id}` - Delete rate

#### Bills
Invoice and billing management:
- `GET /bills` - List all bills
- `POST /bills` - Create new bill
- `GET /bills/{id}` - Get single bill
- `PATCH /bills/{id}` - Update bill
- `DELETE /bills/{id}` - Delete or void bill

#### Contacts
Client and contact management:
- `GET /contacts` - List all contacts
- `POST /contacts` - Create new contact
- `GET /contacts/{id}` - Get single contact
- `PATCH /contacts/{id}` - Update contact
- `DELETE /contacts/{id}` - Delete contact

#### Matters
Case and legal matter management:
- `GET /matters` - List all matters
- `POST /matters` - Create new matter
- `GET /matters/{id}` - Get single matter
- `PATCH /matters/{id}` - Update matter
- `DELETE /matters/{id}` - Delete matter

#### Documents
Document management and storage:
- `GET /documents` - List documents
- `POST /documents` - Upload document
- `GET /documents/{id}` - Get single document
- `PATCH /documents/{id}` - Update document
- `DELETE /documents/{id}` - Delete document

#### Timers
Real-time tracking:
- `GET /timer` - Get active timer
- `POST /timer` - Start new timer
- `DELETE /timer` - Stop timer

#### Custom Actions
UI customization:
- `GET /custom_actions` - List custom actions
- `POST /custom_actions` - Create custom action
- `GET /custom_actions/{id}` - Get single custom action
- `PATCH /custom_actions/{id}` - Update custom action
- `DELETE /custom_actions/{id}` - Delete custom action

#### Webhooks
Event notifications:
- `GET /webhooks` - List webhooks
- `POST /webhooks` - Create webhook
- `GET /webhooks/{id}` - Get single webhook
- `PATCH /webhooks/{id}` - Update webhook
- `DELETE /webhooks/{id}` - Delete webhook

#### Users
User account management:
- `GET /users` - List users
- `GET /users/who_am_i` - Get current user
- `GET /users/{id}` - Get single user
- `PATCH /users/{id}` - Update user

#### Expense Categories
Expense classification:
- `GET /expense_categories` - List categories
- `POST /expense_categories` - Create category
- `GET /expense_categories/{id}` - Get single category
- `PATCH /expense_categories/{id}` - Update category
- `DELETE /expense_categories/{id}` - Delete category

### Common Query Parameters

Most endpoints support these parameters:
- `fields`: Specify response fields
- `page`: Navigate paginated results
- `limit`: Results per page (max 200)
- `order`: Sort results
- `created_since`: Filter by creation date
- `updated_since`: Filter by update date
- `ids[]`: Filter by specific IDs

### Standard Response Format

```json
{
  "data": {
    "id": 123456789,
    "etag": "\"1514daee6390dbbb6a68f6d0d2c36334\"",
    // ... other fields
  }
}
```

For lists:
```json
{
  "data": [
    {
      "id": 123,
      "etag": "\"abc123\"",
      // ... fields
    }
  ],
  "meta": {
    "paging": {
      "next": "https://app.clio.com/api/v4/endpoint?page=2"
    }
  }
}
```

## Clio Grow API (v2)

### Resources

#### Contacts
Lead and contact management in Clio Grow:

**List Contacts**
```
GET /contacts
```
Query parameters:
- `created_since`: Filter by creation date (ISO-8601)
- `ids[]`: Filter by IDs (max 50)
- `page_token`: Pagination token
- `query`: Search name, email, or phone
- `updated_since`: Filter by update date (ISO-8601)

**Get Single Contact**
```
GET /contacts/{id}
```

**Contact Notes**
```
GET /contacts/{contact_id}/notes
POST /contacts/{contact_id}/notes
```

#### Matters
Legal matters in Clio Grow:

**List Matters**
```
GET /matters
```

**Get Single Matter**
```
GET /matters/{id}
```

**Matter Notes**
```
GET /matters/{matter_id}/notes
POST /matters/{matter_id}/notes
```

#### Inbox Leads
Lead management system:

**List Inbox Leads**
```
GET /inbox_leads?state=untriaged
```
Required parameter:
- `state`: "ignored" or "untriaged"

**Create Inbox Lead**
```
POST /inbox_leads
```
Required fields:
- `first_name`: Lead's first name
- `last_name`: Lead's last name  
- `from_message`: Custom message explaining needs
- `from_source`: Integration/service name
- `referring_url`: Source webpage URL

#### Custom Actions
UI customization for Clio Grow:

**List Custom Actions**
```
GET /custom_actions
```

**Create Custom Action**
```
POST /custom_actions
```
Required fields:
- `label`: Link text displayed to users
- `target_url`: Destination URL
- `ui_reference`: Currently "matters/show"

**Security Note**: Custom actions include a `custom_action_nonce` parameter for validation. The nonce expires in 60 seconds and is single-use.

#### Users
User management:

**List Users**
```
GET /users
```

**Get Current User**
```
GET /users/who_am_i
```

### Grow API Response Format

```json
{
  "data": [
    {
      "id": 0,
      "created_at": "2019-08-24T14:15:22Z",
      "updated_at": "2019-08-24T14:15:22Z",
      // ... other fields
    }
  ]
}
```

## Clio Payments API

### Overview
Clio Payments API enables third-party applications to create payment links for collecting payments from clients.

**Requirements:**
- OAuth scope: `clio_payments`
- Clio Payments enabled account
- Connected bank account with `clio_payments_enabled: true`

**Supported Currencies:**
- United States: USD
- Canada: CAD  
- United Kingdom: GBP

### Payment Links

#### Creating Payment Links

**Endpoint:**
```
POST /api/v4/clio_payments/links
```

**Limitations:**
- Maximum duration: 90 days
- Maximum active links: 50 × number of users
- Maximum links per 24 hours: 50 × number of users
- Single-use (expires after payment)

#### Payment Link Types

**1. Pay Existing Invoice/Trust Request**

Required fields:
```json
{
  "data": {
    "currency": "USD",
    "destination_account": {"id": 123456},
    "duration": 86400,
    "subject": {
      "id": 123456,
      "type": "Bill"
    }
  }
}
```

Optional fields:
- `amount`: Fixed payment amount
- `email_address`: Pre-fill client email
- `redirect_url`: Post-payment redirect

**2. Direct Payment Collection**

Required fields:
```json
{
  "data": {
    "currency": "USD",
    "description": "Payment for services",
    "duration": 86400,
    "subject": {
      "id": 123456,
      "type": "BankAccount"
    }
  }
}
```

Optional fields:
- `amount`: Fixed payment amount
- `destination_contact`: Associate with contact
- `email_address`: Pre-fill client email
- `is_allocated_as_revenue`: true for revenue, false for unallocated balance
- `redirect_url`: Post-payment redirect (must match app settings)

#### Retrieving Payment Links

```
GET /api/v4/clio_payment_links
```

Filter parameters:
- `active`: true/false for active/inactive links

Available fields:
- `active`: Link status
- `amount`: Payment amount (if set)
- `bank_account`: Subject for direct payments
- `bill`: Subject for invoice payments
- `contact`: Subject for contact balance payments
- `clio_payments_payment`: Associated payment
- `created_at`: Creation timestamp
- `currency`: Payment currency
- `description`: Payment description
- `destination_account`: Deposit account
- `destination_contact`: Associated contact
- `email_address`: Pre-filled email
- `expires_at`: Expiration timestamp
- `id`: Unique identifier
- `is_allocated_as_revenue`: Revenue allocation flag
- `redirect_url`: Post-payment redirect
- `url`: Payment link URL

#### Retrieving Payment Details

```
GET /api/v4/clio_payments/payments
```

Filter parameters:
- `bill_id`: Associated bill ID
- `contact_id`: Associated contact ID
- `ids`: Array of payment IDs
- `state`: Payment state (authorized, completed, failed, etc.)

Available fields:
- `allocations`: Payment allocations
- `amount`: Payment amount
- `bank_transaction`: Associated bank transaction
- `bills`: Associated bills
- `clio_payments_link`: Source payment link
- `confirmation_number`: Payment confirmation
- `contact`: Associated contact
- `created_at`: Payment timestamp
- `currency`: Payment currency
- `deposit_as_revenue`: Revenue flag
- `description`: Payment description
- `destination_account`: Deposit account
- `email_address`: Client email
- `id`: Unique identifier
- `matters`: Associated matters
- `state`: Payment state
- `updated_at`: Last update timestamp
- `user`: Creating user

### Webhooks Integration

Use the Webhooks API to receive payment notifications:
- Event: `clio_payments_payment`
- Triggers: Payment created or updated
- Note: Deleted events not supported (payments cannot be deleted)

## Personal Injury API

The Personal Injury API provides specialized endpoints for personal injury practice management, extending the core Clio Manage API with industry-specific features.

*Note: Specific endpoints and documentation for Personal Injury API features should be referenced from the official Clio developer documentation.*

## Webhooks

Webhooks provide real-time notifications when data changes in Clio.

### Webhook Management

```
GET /api/v4/webhooks      # List webhooks
POST /api/v4/webhooks     # Create webhook  
GET /api/v4/webhooks/{id} # Get webhook
PATCH /api/v4/webhooks/{id} # Update webhook
DELETE /api/v4/webhooks/{id} # Delete webhook
```

### Supported Events

Webhooks support various events for different resources:
- Resource creation events
- Resource update events
- Resource deletion events (where applicable)
- Specialized events (e.g., `clio_payments_payment`)

### Security

Webhook payloads should be verified using signature validation to ensure authenticity and integrity of the data received.

## Best Practices

### Error Handling
- Implement robust error handling for all API calls
- Handle rate limiting with exponential backoff
- Use appropriate HTTP status code responses

### Security
- Never log or expose authentication tokens
- Use HTTPS for all API communications
- Validate webhook signatures
- Follow SOC 2 Type 2 and HIPAA compliance guidelines

### Performance
- Use field selection to minimize response size
- Implement appropriate caching strategies with ETags
- Handle pagination properly for large datasets
- Respect rate limits and implement backoff strategies

### Data Management
- Use ETags for conditional updates
- Handle data conflicts gracefully
- Implement proper data validation
- Follow legal data retention requirements

## Support and Resources

### Developer Support
- **API Issues**: [api@clio.com](mailto:api@clio.com)
- **Business Partnerships**: [api.partnerships@clio.com](mailto:api.partnerships@clio.com)
- **Community**: [Clio Developer Slack Channel](https://join.slack.com/t/clio-public/shared_invite/zt-36i0eqgo1-7POORPtMJpp2N0~_auL2IQ)

### Documentation Links
- **Main Documentation**: https://docs.developers.clio.com
- **API Reference**: https://docs.developers.clio.com/api-reference/
- **Grow API Reference**: https://docs.developers.clio.com/grow-api/api-reference
- **Developer Handbook**: https://docs.developers.clio.com/handbook/

### Regional Developer Portals
- **US**: https://developers.clio.com/
- **EU**: https://eu.developers.clio.com/
- **AU**: https://au.developers.clio.com/

---

*This comprehensive documentation was compiled from the official Clio developer documentation. For the most up-to-date information and detailed endpoint specifications, please refer to the official documentation at https://docs.developers.clio.com*