import { getSession } from '@auth0/nextjs-auth0';
import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.API_URL || 'http://backend:8000/api/v1';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyRequest(request, resolvedParams.path, 'GET');
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyRequest(request, resolvedParams.path, 'POST');
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyRequest(request, resolvedParams.path, 'PATCH');
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> }
) {
  const resolvedParams = await params;
  return proxyRequest(request, resolvedParams.path, 'DELETE');
}

async function proxyRequest(
  request: NextRequest,
  pathSegments: string[],
  method: string
) {
  try {
    // Get session without parameters for App Router
    const session = await getSession();

    if (!session || !session.user) {
      return NextResponse.json(
        { error: 'Unauthorized' },
        { status: 401 }
      );
    }

    // Get the user's Auth0 ID
    const auth0Id = session.user.sub;

    // Build the backend URL
    const path = pathSegments.join('/');
    const searchParams = request.nextUrl.searchParams.toString();
    const backendUrl = `${BACKEND_URL}/api/v1/${path}${searchParams ? `?${searchParams}` : ''}`;

    // Prepare headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // Pass the Auth0 user ID as a custom header for now
      'X-User-Sub': auth0Id,
    };

    // Get request body for POST/PATCH
    let body = undefined;
    if (method === 'POST' || method === 'PATCH') {
      const text = await request.text();
      body = text || undefined;
    }

    // Make request to backend
    const response = await fetch(backendUrl, {
      method,
      headers,
      body,
    });

    // Get response data
    const data = await response.text();

    // Create response with same status code
    return new NextResponse(data, {
      status: response.status,
      headers: {
        'Content-Type': response.headers.get('Content-Type') || 'application/json',
      },
    });

  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export const dynamic = 'force-dynamic';
