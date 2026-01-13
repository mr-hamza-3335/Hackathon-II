/**
 * Landing page with redirect logic.
 * T092: Create landing page in frontend/src/app/page.tsx with redirect logic based on auth status
 */

import { redirect } from 'next/navigation';
import { cookies } from 'next/headers';

export default function Home() {
  const cookieStore = cookies();
  const authToken = cookieStore.get('auth_token');

  if (authToken) {
    redirect('/dashboard');
  } else {
    redirect('/login');
  }
}
