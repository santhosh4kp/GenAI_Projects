# Day 3: Adding User Authentication with Clerk

## Transform Your SaaS with Professional Authentication

Today you'll add enterprise-grade authentication to your Business Idea Generator, allowing users to sign in with Google, GitHub, and other providers. This transforms your app from a demo into a real SaaS product.

## What You'll Build

An authenticated version of your app that:
- Requires users to sign in before accessing the idea generator
- Supports multiple authentication providers (Google, GitHub, Email)
- Passes secure JWT tokens to your backend
- Verifies user identity on every API request
- Works seamlessly with Next.js Pages Router

## Prerequisites

- Completed Day 2 (working Business Idea Generator)
- Your project deployed to Vercel

## Part 1: User Authentication

### Step 1: Create Your Clerk Account

1. Visit [clerk.com](https://clerk.com) and click **Sign Up**
2. Create your account using Google auth (or your preferred method)
3. You'll be taken to **Create Application** (or click "Create Application" if returning)

### Step 2: Configure Your Clerk Application

1. **Application name:** SaaS
2. **Sign-in options:** Enable these providers:
   - Email
   - Google  
   - GitHub
   - Apple (optional)
3. Click **Create Application**

You'll see the Clerk dashboard with your API keys displayed.

### Step 3: Install Clerk Dependencies

In your terminal, install the Clerk SDK:

```bash
npm install @clerk/nextjs
```

For handling streaming with authentication, also install:

```bash
npm install @microsoft/fetch-event-source
```

### Step 4: Configure Environment Variables

Create a `.env.local` file in your project root:

```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_publishable_key_here
CLERK_SECRET_KEY=your_secret_key_here
```

**Important:** Copy these values from the Clerk dashboard (they're displayed after creating your application on the configure screen).

### Add to .gitignore

Open `.gitignore` in Cursor and add `.env.local` on a new line.

### Step 5: Add Clerk Provider to Your App

With Pages Router, we need to wrap our application with the Clerk provider. Update `pages/_app.tsx`:

```typescript
import { ClerkProvider } from '@clerk/nextjs';
import type { AppProps } from 'next/app';
import '../styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}
```

### Step 6: Create the Product Page

Move your business idea generator to a protected route. Since we're using client-side authentication, we'll protect this route using Clerk's built-in components.

Create `pages/product.tsx`:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';

export default function Product() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        let buffer = '';
        (async () => {
            const jwt = await getToken();
            if (!jwt) {
                setIdea('Authentication required');
                return;
            }
            
            await fetchEventSource('/api', {
                headers: { Authorization: `Bearer ${jwt}` },
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    // Don't throw - let it retry
                }
            });
        })();
    }, []); // Empty dependency array - run once on mount

    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            <div className="container mx-auto px-4 py-12">
                {/* Header */}
                <header className="text-center mb-12">
                    <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                        Business Idea Generator
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 text-lg">
                        AI-powered innovation at your fingertips
                    </p>
                </header>

                {/* Content Card */}
                <div className="max-w-3xl mx-auto">
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                        {idea === '…loading' ? (
                            <div className="flex items-center justify-center py-12">
                                <div className="animate-pulse text-gray-400">
                                    Generating your business idea...
                                </div>
                            </div>
                        ) : (
                            <div className="markdown-content text-gray-700 dark:text-gray-300">
                                <ReactMarkdown
                                    remarkPlugins={[remarkGfm, remarkBreaks]}
                                >
                                    {idea}
                                </ReactMarkdown>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}
```

### Step 7: Create the Landing Page

Update `pages/index.tsx` to be your new landing page with sign-in:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            IdeaGen
          </h1>
          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link 
                  href="/product" 
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Generate Your Next
            <br />
            Big Business Idea
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            Harness the power of AI to discover innovative business opportunities tailored for the AI agent economy
          </p>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Get Started Free
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Generate Ideas Now
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}
```

### Step 8: Configure Backend Authentication

First, get your JWKS URL from Clerk:
1. Go to your Clerk Dashboard
2. Click **Configure** (top nav)
3. Click **API Keys** (side nav)  
4. Find **JWKS URL** and copy it

**What is JWKS?** The JWKS (JSON Web Key Set) URL is a public endpoint that contains Clerk's public keys. When a user signs in, Clerk creates a JWT (JSON Web Token) - a digitally signed token that proves the user's identity. Your Python backend uses the JWKS URL to fetch Clerk's public keys and verify that incoming JWT tokens are genuine and haven't been tampered with. This allows secure authentication without your backend needing to contact Clerk for every request - it can verify tokens independently using cryptographic signatures.

Add to `.env.local`:
```bash
CLERK_JWKS_URL=your_jwks_url_here
```

### Step 9: Update Backend Dependencies

Add the Clerk authentication library to `requirements.txt`:

```
fastapi
uvicorn
groq
fastapi-clerk-auth
```

### Step 10: Update the API with Authentication

Replace `api/index.py` with:

```python
from fastapi import FastAPI, Depends
from fastapi.responses import StreamingResponse
from groq import Groq

import os
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

app = FastAPI()

clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)

@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]

    message = "Come up with a new business idea for AI Agents"

    stream = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": message}],
        stream=True
    )
    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"
    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

### Step 11: Add Environment Variables to Vercel

Add your Clerk keys to Vercel:

```bash
vercel env add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
```
Paste your publishable key and select all environments.

```bash
vercel env add CLERK_SECRET_KEY
```
Paste your secret key and select all environments.

```bash
vercel env add CLERK_JWKS_URL
```
Paste your JWKS URL and select all environments.

Add your groq API keys to Vercel:

```bash
vercel env add GROQ_API_KEY
```

### Step 12: Test Locally

Test your authentication locally:

```bash
vercel dev
```

**Note:** The Python backend won't work locally with `vercel dev`, but the authentication flow will work perfectly! You'll be able to sign in, sign out, and see the user interface.

Visit `http://localhost:3000` and:
1. Click "Sign In"
2. Create an account or sign in with Google/GitHub
3. You'll be redirected to the landing page, now authenticated
4. Click "Go to App" to access the protected idea generator

### Step 13: Deploy to Production

Deploy your authenticated app:

```bash
vercel --prod
```

Visit your production URL and test the complete authentication flow!

NOTE - if you hit a problem with jwt token expiration, please see this [fix contributed by Artur P](../community_contributions/arturp_jwt_token_fix_notes.md)

## What's Happening?

Your app now has:
- **Secure authentication**: Users must sign in to access your product
- **Client-side route protection**: Unauthenticated users are redirected from protected pages
- **JWT verification**: Every API request is verified using cryptographic signatures
- **User identification**: The backend knows which user is making each request
- **Professional UX**: Modal sign-in, user profile management, and smooth redirects
- **Multiple providers**: Users can choose their preferred sign-in method

## Security Architecture

Since we're using client-side Next.js with a separate Python backend:

1. **Frontend (Browser)**: User signs in with Clerk → receives session token
2. **Client-Side Protection**: Protected routes check authentication status and redirect if needed
3. **API Request**: Browser sends JWT token directly to Python backend with each request
4. **Backend Verification**: FastAPI verifies the JWT using Clerk's public keys (JWKS)
5. **User Context**: Backend can access user ID and metadata from verified token

This architecture keeps your Next.js deployment simple (static/client-side only) while maintaining secure API authentication.

## Troubleshooting

### "Unauthorized" errors
- Check that all three environment variables are set correctly in Vercel
- Ensure the JWKS URL is copied correctly from Clerk
- Verify you're signed in before accessing `/product`

### Sign-in modal not appearing
- Check that `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` starts with `pk_`
- Ensure you've wrapped your app with `ClerkProvider`
- Clear browser cache and cookies

### API not authenticating
- Verify `CLERK_JWKS_URL` is set in your environment
- Check that `fastapi-clerk-auth` is in requirements.txt
- Ensure the JWT token is being sent in the Authorization header

### Local development issues
- Make sure `.env.local` has all three Clerk variables
- Restart your dev server after adding environment variables
- Try clearing Next.js cache: `rm -rf .next`

## Next Steps

Congratulations! You've added professional authentication to your SaaS. In Part 2, we'll add:
- Subscription tiers with Stripe
- Usage limits based on subscription level
- Payment processing
- Customer portal for managing subscriptions

Your app is now a real SaaS product with secure user authentication!


# Day 3 Part 2: Adding Subscriptions with Clerk Billing

## Transform Your SaaS with Subscription Management

Now let's add subscription tiers to your Business Idea Generator, turning it into a full-fledged SaaS with payment processing and subscription management built-in.

## What You'll Build

An enhanced version of your app that:
- Requires a paid subscription to access the idea generator
- Shows a beautiful pricing table to non-subscribers
- Handles payment processing through Clerk Billing
- Manages subscription status automatically
- Provides a user menu with billing management options

## Prerequisites

- Completed Day 3 Part 1 (authentication working)
- Your app deployed to Vercel

## Step 1: Enable Clerk Billing

### Navigate to Clerk Dashboard

1. Go to your [Clerk Dashboard](https://dashboard.clerk.com)
2. Select your **SaaS** application
3. Click **Configure** in the top navigation
4. Click **Subscription Plans** in the left sidebar
5. Click **Get Started** if this is your first time

### Enable Billing

1. Click **Enable Billing** if prompted
2. Accept the terms if prompted
3. You'll see the Subscription Plans page

## Step 2: Create Your Subscription Plan

### Configure the Plan

1. Click **Create Plan**
2. Fill in the details:
   - **Name:** Premium Subscription
   - **Key:** `premium_subscription` (this is important - copy it exactly)
   - **Price:** $10.00 monthly (or your preferred price)
   - **Description:** Unlimited AI-powered business ideas
3. Optional: Add an annual discount
   - Toggle on **Annual billing**
   - Set annual price (e.g., $100/year for a discount)
4. Click **Save**

### Copy the Plan ID

After creating the plan, you'll see a **Plan ID** in the top right of the plan card (it looks like `plan_...`). You'll need this for testing, but Clerk handles it automatically in production.

## Step 3: Update Your Product Page

Since we're using Pages Router with client-side components, we need to protect our product route with the subscription check.

Update `pages/product.tsx`:

```typescript
"use client"

import { useEffect, useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { useAuth } from '@clerk/nextjs';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { Protect, PricingTable, UserButton } from '@clerk/nextjs';

function IdeaGenerator() {
    const { getToken } = useAuth();
    const [idea, setIdea] = useState<string>('…loading');

    useEffect(() => {
        let buffer = '';
        (async () => {
            const jwt = await getToken();
            if (!jwt) {
                setIdea('Authentication required');
                return;
            }
            
            await fetchEventSource('/api', {
                headers: { Authorization: `Bearer ${jwt}` },
                onmessage(ev) {
                    buffer += ev.data;
                    setIdea(buffer);
                },
                onerror(err) {
                    console.error('SSE error:', err);
                    // Don't throw - let it retry
                }
            });
        })();
    }, []); // Empty dependency array - run once on mount

    return (
        <div className="container mx-auto px-4 py-12">
            {/* Header */}
            <header className="text-center mb-12">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                    Business Idea Generator
                </h1>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    AI-powered innovation at your fingertips
                </p>
            </header>

            {/* Content Card */}
            <div className="max-w-3xl mx-auto">
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 backdrop-blur-lg bg-opacity-95">
                    {idea === '…loading' ? (
                        <div className="flex items-center justify-center py-12">
                            <div className="animate-pulse text-gray-400">
                                Generating your business idea...
                            </div>
                        </div>
                    ) : (
                        <div className="markdown-content text-gray-700 dark:text-gray-300">
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm, remarkBreaks]}
                            >
                                {idea}
                            </ReactMarkdown>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default function Product() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
            {/* User Menu in Top Right */}
            <div className="absolute top-4 right-4">
                <UserButton showName={true} />
            </div>

            {/* Subscription Protection */}
            <Protect
                plan="premium_subscription"
                fallback={
                    <div className="container mx-auto px-4 py-12">
                        <header className="text-center mb-12">
                            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                                Choose Your Plan
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8">
                                Unlock unlimited AI-powered business ideas
                            </p>
                        </header>
                        <div className="max-w-4xl mx-auto">
                            <PricingTable />
                        </div>
                    </div>
                }
            >
                <IdeaGenerator />
            </Protect>
        </main>
    );
}
```

## Step 4: Update Your Landing Page

Let's update the landing page to better reflect the subscription model.

Update `pages/index.tsx`:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            IdeaGen Pro
          </h1>
          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link 
                  href="/product" 
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-24">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Generate Your Next
            <br />
            Big Business Idea
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-8 max-w-2xl mx-auto">
            Harness the power of AI to discover innovative business opportunities tailored for the AI agent economy
          </p>
          
          {/* Pricing Preview */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl p-6 max-w-sm mx-auto mb-8">
            <h3 className="text-2xl font-bold mb-2">Premium Subscription</h3>
            <p className="text-4xl font-bold text-blue-600 mb-2">$10<span className="text-lg text-gray-600">/month</span></p>
            <ul className="text-left text-gray-600 dark:text-gray-400 mb-6">
              <li className="mb-2">✓ Unlimited idea generation</li>
              <li className="mb-2">✓ Advanced AI models</li>
              <li className="mb-2">✓ Priority support</li>
            </ul>
          </div>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Your Free Trial
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Access Premium Features
              </button>
            </Link>
          </SignedIn>
        </div>
      </div>
    </main>
  );
}
```

## Step 5: Configure Billing Provider (Optional)

Clerk comes with a built-in payment gateway that's ready to use immediately:

1. In Clerk Dashboard → **Configure** → **Billing** → **Settings** (in the left sidebar)
2. By default, **Clerk payment gateway** is selected:
   - "Our zero-config payment gateway. Ready to process test payments immediately."
   - This works great for testing and development
3. **Optional:** You can switch to Stripe if you prefer:
   - Select **Stripe** instead
   - Follow Clerk's setup wizard to connect your Stripe account

**Note:** The Clerk payment gateway is perfect for getting started - it handles test payments immediately without any additional setup.

## Step 6: Test Your Subscription Flow

Deploy your updated application:

```bash
vercel --prod
```

### Testing the Flow

1. Visit your production URL
2. Sign in (or create a new account)
3. Click "Go to App" or "Access Premium Features"
4. You'll see the pricing table since you don't have a subscription
5. Click **Subscribe** on the Premium plan
6. If you haven't connected a payment provider, Clerk will simulate the subscription
7. After subscribing, you'll have access to the idea generator

### Managing Subscriptions

Users can manage their subscriptions through the UserButton menu:
1. Click on their profile picture (UserButton)
2. Select **Manage account**
3. Navigate to **Subscriptions**
4. View or cancel their subscription

## What's Happening?

Your app now has:
- **Subscription Gate**: Users must have an active subscription to access the product
- **Pricing Table**: Beautiful, Clerk-managed pricing display
- **Payment Processing**: Handled entirely by Clerk (with Stripe integration if configured)
- **User Management**: Subscription status in the UserButton menu
- **Automatic Enforcement**: Clerk automatically checks subscription status

## Architecture Overview

1. **User visits `/product`** → Clerk checks subscription status
2. **No subscription** → Shows PricingTable component
3. **Has subscription** → Shows IdeaGenerator component
4. **Payment** → Handled by Clerk Billing (optionally with Stripe)
5. **Management** → Users manage subscriptions through Clerk's UI

## Troubleshooting

### "Plan not found" error
- Ensure the plan key is exactly `premium_subscription`
- Check that billing is enabled in Clerk Dashboard
- Verify the plan is active (not archived)

### Pricing table not showing
- Clear browser cache and cookies
- Check that `@clerk/nextjs` is up to date
- Ensure billing is enabled in your Clerk application

### Always seeing the pricing table (even after subscribing)
- Check the user's subscription status in Clerk Dashboard
- Verify the plan key matches exactly
- Try signing out and back in

### Payment not working
- This is normal if you haven't connected a payment provider
- Clerk will simulate subscriptions in test mode
- For real payments, connect Stripe in Billing Settings

## Customization Options

### Different Plan Tiers

You can create multiple plans in Clerk Dashboard:
```typescript
<Protect
    plan={["basic_plan", "premium_plan", "enterprise_plan"]}
    fallback={<PricingTable />}
>
    <IdeaGenerator />
</Protect>
```

### Custom Pricing Table

Instead of Clerk's default PricingTable, you can build your own:
```typescript
<Protect
    plan="premium_subscription"
    fallback={<CustomPricingPage />}
>
    <IdeaGenerator />
</Protect>
```

### Usage Limits

Track API usage per user in your backend:
```python
@app.get("/api")
def idea(creds: HTTPAuthorizationCredentials = Depends(clerk_guard)):
    user_id = creds.decoded["sub"]
    subscription_plan = creds.decoded.get("subscription", "free")
    
    # Apply different limits based on plan
    if subscription_plan == "premium_subscription":
        # Unlimited or high limit
        pass
    else:
        # Limited access
        pass
```

## Next Steps

Congratulations! You've built a complete SaaS with:
- ✅ User authentication
- ✅ Subscription management
- ✅ Payment processing
- ✅ AI-powered features
- ✅ Professional UI/UX

### Ideas for Enhancement

1. **Multiple subscription tiers** (Basic, Pro, Enterprise)
2. **Usage tracking** and limits per tier
3. **Webhook integration** for subscription events
4. **Email notifications** for subscription changes
5. **Admin dashboard** to manage users and subscriptions
6. **Annual billing discounts**
7. **Free trial periods**

Your Business Idea Generator is now a fully-functional SaaS product ready for real customers!


# Day 4: Healthcare Consultation Assistant

## Build a Professional Healthcare Application

Today, you'll transform your SaaS into a healthcare consultation assistant that helps doctors generate patient summaries, action items, and patient-friendly emails from their visit notes.

## What You'll Build

A healthcare application that:
- Takes doctor's consultation notes as input
- Generates professional summaries for medical records
- Creates actionable next steps for the doctor
- Drafts patient-friendly email communications
- Uses structured forms with date pickers
- Streams AI-generated content in real-time

## Prerequisites

- Completed Day 3 (authentication and subscriptions working)
- Your app deployed to Vercel

## Step 1: Install Additional Dependencies

We need a date picker for the consultation form:

```bash
npm install react-datepicker
npm install --save-dev @types/react-datepicker
```

## Step 2: Update the Backend API

Replace `api/index.py` with a new endpoint that handles consultation data:

```python
import os
from fastapi import FastAPI, Depends  # type: ignore
from fastapi.responses import StreamingResponse  # type: ignore
from pydantic import BaseModel  # type: ignore
from fastapi_clerk_auth import ClerkConfig, ClerkHTTPBearer, HTTPAuthorizationCredentials  # type: ignore
from openai import OpenAI  # type: ignore

app = FastAPI()
clerk_config = ClerkConfig(jwks_url=os.getenv("CLERK_JWKS_URL"))
clerk_guard = ClerkHTTPBearer(clerk_config)


class Visit(BaseModel):
    patient_name: str
    date_of_visit: str
    notes: str


system_prompt = """
You are provided with notes written by a doctor from a patient's visit.
Your job is to summarize the visit for the doctor and provide an email.
Reply with exactly three sections with the headings:
### Summary of visit for the doctor's records
### Next steps for the doctor
### Draft of email to patient in patient-friendly language
"""


def user_prompt_for(visit: Visit) -> str:
    return f"""Create the summary, next steps and draft email for:
Patient Name: {visit.patient_name}
Date of Visit: {visit.date_of_visit}
Notes:
{visit.notes}"""


@app.post("/api")
def consultation_summary(
    visit: Visit,
    creds: HTTPAuthorizationCredentials = Depends(clerk_guard),
):
    user_id = creds.decoded["sub"]  # Available for tracking/auditing
    client = OpenAI()

    user_prompt = user_prompt_for(visit)

    prompt = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=prompt,
        stream=True,
    )

    def event_stream():
        for chunk in stream:
            text = chunk.choices[0].delta.content
            if text:
                lines = text.split("\n")
                for line in lines[:-1]:
                    yield f"data: {line}\n\n"
                    yield "data:  \n"
                yield f"data: {lines[-1]}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
```

Note the key changes:
- Changed from `@app.get("/api")` to `@app.post("/api")` to accept form data
- Added a `Visit` model to validate incoming data
- Structured prompts for healthcare-specific output

## Step 3: Update Application Configuration

First, import the date picker styles in `pages/_app.tsx`:

```typescript
import { ClerkProvider } from '@clerk/nextjs';
import type { AppProps } from 'next/app';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/globals.css';

export default function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ClerkProvider {...pageProps}>
      <Component {...pageProps} />
    </ClerkProvider>
  );
}
```

Now update `pages/_document.tsx` to reflect the healthcare focus:

```typescript
import { Html, Head, Main, NextScript } from 'next/document';

export default function Document() {
  return (
    <Html lang="en">
      <Head>
        <title>Healthcare Consultation Assistant</title>
        <meta name="description" content="AI-powered medical consultation summaries" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  );
}
```

## Step 4: Create the Consultation Form

Replace `pages/product.tsx` with the new healthcare interface:

```typescript
"use client"

import { useState, FormEvent } from 'react';
import { useAuth } from '@clerk/nextjs';
import DatePicker from 'react-datepicker';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkBreaks from 'remark-breaks';
import { fetchEventSource } from '@microsoft/fetch-event-source';
import { Protect, PricingTable, UserButton } from '@clerk/nextjs';

function ConsultationForm() {
    const { getToken } = useAuth();

    // Form state
    const [patientName, setPatientName] = useState('');
    const [visitDate, setVisitDate] = useState<Date | null>(new Date());
    const [notes, setNotes] = useState('');

    // Streaming state
    const [output, setOutput] = useState('');
    const [loading, setLoading] = useState(false);

    async function handleSubmit(e: FormEvent) {
        e.preventDefault();
        setOutput('');
        setLoading(true);

        const jwt = await getToken();
        if (!jwt) {
            setOutput('Authentication required');
            setLoading(false);
            return;
        }

        const controller = new AbortController();
        let buffer = '';

        await fetchEventSource('/api', {
            signal: controller.signal,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${jwt}`,
            },
            body: JSON.stringify({
                patient_name: patientName,
                date_of_visit: visitDate?.toISOString().slice(0, 10),
                notes,
            }),
            onmessage(ev) {
                buffer += ev.data;
                setOutput(buffer);
            },
            onclose() { 
                setLoading(false); 
            },
            onerror(err) {
                console.error('SSE error:', err);
                controller.abort();
                setLoading(false);
            },
        });
    }

    return (
        <div className="container mx-auto px-4 py-12 max-w-3xl">
            <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-8">
                Consultation Notes
            </h1>

            <form onSubmit={handleSubmit} className="space-y-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
                <div className="space-y-2">
                    <label htmlFor="patient" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Patient Name
                    </label>
                    <input
                        id="patient"
                        type="text"
                        required
                        value={patientName}
                        onChange={(e) => setPatientName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="Enter patient's full name"
                    />
                </div>

                <div className="space-y-2">
                    <label htmlFor="date" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Date of Visit
                    </label>
                    <DatePicker
                        id="date"
                        selected={visitDate}
                        onChange={(d: Date | null) => setVisitDate(d)}
                        dateFormat="yyyy-MM-dd"
                        placeholderText="Select date"
                        required
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    />
                </div>

                <div className="space-y-2">
                    <label htmlFor="notes" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                        Consultation Notes
                    </label>
                    <textarea
                        id="notes"
                        required
                        rows={8}
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="Enter detailed consultation notes..."
                    />
                </div>

                <button 
                    type="submit" 
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200"
                >
                    {loading ? 'Generating Summary...' : 'Generate Summary'}
                </button>
            </form>

            {output && (
                <section className="mt-8 bg-gray-50 dark:bg-gray-800 rounded-xl shadow-lg p-8">
                    <div className="markdown-content prose prose-blue dark:prose-invert max-w-none">
                        <ReactMarkdown remarkPlugins={[remarkGfm, remarkBreaks]}>
                            {output}
                        </ReactMarkdown>
                    </div>
                </section>
            )}
        </div>
    );
}

export default function Product() {
    return (
        <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
            {/* User Menu in Top Right */}
            <div className="absolute top-4 right-4">
                <UserButton showName={true} />
            </div>

            {/* Subscription Protection */}
            <Protect
                plan="premium_subscription"
                fallback={
                    <div className="container mx-auto px-4 py-12">
                        <header className="text-center mb-12">
                            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-4">
                                Healthcare Professional Plan
                            </h1>
                            <p className="text-gray-600 dark:text-gray-400 text-lg mb-8">
                                Streamline your patient consultations with AI-powered summaries
                            </p>
                        </header>
                        <div className="max-w-4xl mx-auto">
                            <PricingTable />
                        </div>
                    </div>
                }
            >
                <ConsultationForm />
            </Protect>
        </main>
    );
}
```

## Step 5: Update the Landing Page

Update `pages/index.tsx` to reflect the healthcare focus:

```typescript
"use client"

import Link from 'next/link';
import { SignInButton, SignedIn, SignedOut, UserButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-12">
        {/* Navigation */}
        <nav className="flex justify-between items-center mb-12">
          <h1 className="text-2xl font-bold text-gray-800 dark:text-gray-200">
            MediNotes Pro
          </h1>
          <div>
            <SignedOut>
              <SignInButton mode="modal">
                <button className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors">
                  Sign In
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-4">
                <Link 
                  href="/product" 
                  className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-6 rounded-lg transition-colors"
                >
                  Go to App
                </Link>
                <UserButton showName={true} />
              </div>
            </SignedIn>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="text-center py-16">
          <h2 className="text-6xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent mb-6">
            Transform Your
            <br />
            Consultation Notes
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-400 mb-12 max-w-2xl mx-auto">
            AI-powered assistant that generates professional summaries, action items, and patient communications from your consultation notes
          </p>

          {/* Features Grid */}
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto mb-12">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-cyan-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">📋</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Professional Summaries</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Generate comprehensive medical record summaries from your notes
                </p>
              </div>
            </div>
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-emerald-600 to-green-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">✅</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Action Items</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Clear next steps and follow-up actions for every consultation
                </p>
              </div>
            </div>
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl blur opacity-25 group-hover:opacity-40 transition duration-300"></div>
              <div className="relative bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 backdrop-blur-sm">
                <div className="text-3xl mb-4">📧</div>
                <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-gray-100">Patient Emails</h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Draft clear, patient-friendly email communications automatically
                </p>
              </div>
            </div>
          </div>
          
          <SignedOut>
            <SignInButton mode="modal">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Start Free Trial
              </button>
            </SignInButton>
          </SignedOut>
          <SignedIn>
            <Link href="/product">
              <button className="bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-xl text-lg transition-all transform hover:scale-105">
                Open Consultation Assistant
              </button>
            </Link>
          </SignedIn>
        </div>

        {/* Trust Indicators */}
        <div className="text-center text-sm text-gray-500 dark:text-gray-400">
          <p>HIPAA Compliant • Secure • Professional</p>
        </div>
      </div>
    </main>
  );
}
```

## Step 6: Update Backend Dependencies

Make sure `requirements.txt` includes Pydantic for data validation:

```
fastapi
uvicorn
openai
fastapi-clerk-auth
pydantic
```

## Step 7: Deploy Your Healthcare App

Deploy your transformed application:

```bash
vercel --prod
```

## Step 8: Test the Consultation Flow

1. Visit your production URL
2. Sign in with your account
3. Navigate to the consultation form
4. Try entering sample consultation notes:

**Example Input:**
- **Patient Name:** Jane Smith
- **Date:** Today's date
- **Notes:** 
  ```
  Patient presents with persistent cough for 2 weeks. No fever. 
  Chest clear on examination. Blood pressure 120/80. 
  Likely viral bronchitis. Prescribed rest and fluids. 
  Follow up if symptoms persist beyond another week.
  ```

You'll receive:
1. A professional summary for medical records
2. Clear next steps for the doctor
3. A patient-friendly email draft

## What's Happening?

Your healthcare app now:
- **Accepts structured input**: Form data with patient name, date, and notes
- **Validates data**: Using Pydantic models on the backend
- **Generates structured output**: Three distinct sections for different purposes
- **Maintains security**: All data is transmitted with JWT authentication
- **Supports subscriptions**: Only premium users can access the tool

## Architecture Changes from Day 3

1. **POST instead of GET**: The API now accepts form data via POST requests
2. **Structured prompts**: System and user prompts guide the AI output format
3. **Form validation**: Both frontend (required fields) and backend (Pydantic) validation
4. **Date handling**: Proper date picker with ISO format conversion
5. **Professional UI**: Healthcare-focused design with clear sections

## Security Considerations

**Important:** This is a demonstration application. For production healthcare use:
- Implement proper HIPAA compliance measures
- Add data encryption at rest and in transit
- Implement audit logging for all access
- Add role-based access control (doctor vs admin)
- Ensure proper data retention policies
- Add patient consent management

## Troubleshooting

### "Method not allowed" error
- Make sure the API endpoint uses `@app.post("/api")` not `@app.get("/api")`
- Verify the fetch request uses `method: 'POST'`

### Date picker not styled correctly
- Ensure `react-datepicker/dist/react-datepicker.css` is imported in `pages/_app.tsx`
- Check that the date picker has the correct className for Tailwind styling

### Form data not sending
- Check browser console for errors
- Verify all required fields are filled
- Ensure the JWT token is being retrieved successfully

### Output not formatting correctly
- Make sure the markdown-content styles are applied (from Day 2)
- Verify ReactMarkdown plugins are imported

## Customization Ideas

### Add More Fields
```typescript
// Add specialty selection
const [specialty, setSpecialty] = useState('General Practice');

// Add urgency level
const [urgency, setUrgency] = useState<'routine' | 'urgent' | 'emergency'>('routine');
```

### Enhanced Templates
Create different prompt templates for different specialties:
```python
def get_system_prompt(specialty: str) -> str:
    prompts = {
        "cardiology": "Focus on cardiac symptoms and cardiovascular health...",
        "pediatrics": "Use child-friendly language in patient communications...",
        "psychiatry": "Include mental health considerations and resources..."
    }
    return prompts.get(specialty, system_prompt)
```

### Export Options
Add buttons to export the generated content:
```typescript
const handleExportPDF = () => {
    // Generate PDF from markdown
};

const handleCopyEmail = () => {
    // Copy email section to clipboard
};
```

## Next Steps

Congratulations! You've built a professional healthcare consultation assistant with:
- ✅ Structured medical data input
- ✅ AI-powered content generation
- ✅ Professional and patient-friendly outputs
- ✅ Secure authentication and subscriptions
- ✅ Modern, accessible UI

### Potential Enhancements

1. **Template library**: Pre-built templates for common conditions
2. **Voice input**: Dictation support for notes
3. **Multi-language**: Support for patient emails in different languages
4. **Integration**: Connect with EHR systems
5. **Analytics**: Track consultation patterns and time saved
6. **Collaboration**: Allow multiple doctors to share templates

Your healthcare assistant is ready to help medical professionals save time and improve patient communication!