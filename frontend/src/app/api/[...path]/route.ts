import { type NextRequest, NextResponse } from "next/server";

function getBackendOrigin(): string {
  const explicitUrl = process.env.BACKEND_URL?.trim().replace(/\/+$/, "");
  if (explicitUrl) {
    return explicitUrl;
  }

  const host = process.env.BACKEND_HOST?.trim().replace(/\/+$/, "");
  if (host) {
    return host.startsWith("http://") || host.startsWith("https://")
      ? host
      : `https://${host}`;
  }

  const publicUrl = process.env.NEXT_PUBLIC_API_BASE_URL?.trim().replace(/\/+$/, "");
  if (publicUrl) {
    return publicUrl;
  }

  return "http://127.0.0.1:5001";
}

async function proxyRequest(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
): Promise<NextResponse> {
  const { path } = await context.params;
  const targetUrl = new URL(
    `/api/${path.join("/")}${request.nextUrl.search}`,
    getBackendOrigin()
  );

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  const accept = request.headers.get("accept");
  const cookie = request.headers.get("cookie");
  if (contentType) headers.set("content-type", contentType);
  if (accept) headers.set("accept", accept);
  if (cookie) headers.set("cookie", cookie);

  const method = request.method.toUpperCase();
  const body =
    method === "GET" || method === "HEAD" ? undefined : await request.text();

  try {
    const upstream = await fetch(targetUrl, {
      method,
      headers,
      body,
      cache: "no-store",
    });

    const responseText = await upstream.text();
    const res = new NextResponse(responseText, {
      status: upstream.status,
      headers: {
        "content-type": upstream.headers.get("content-type") ?? "application/json",
      },
    });

    const setCookie = upstream.headers.get("set-cookie");
    if (setCookie) {
      res.headers.set("set-cookie", setCookie);
    }

    return res;
  } catch (error) {
    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? `Backend proxy error: ${error.message}`
            : "Backend service unavailable",
      },
      { status: 502 }
    );
  }
}

export async function GET(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, context);
}

export async function POST(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, context);
}

export async function DELETE(
  request: NextRequest,
  context: { params: Promise<{ path: string[] }> }
) {
  return proxyRequest(request, context);
}

