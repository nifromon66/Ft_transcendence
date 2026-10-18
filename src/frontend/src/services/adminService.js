import { useAuthStore } from '@/stores/authState'

const baseUrl = import.meta.env.VITE_API_URL || ''

export async function adminRequest(path, { method = 'GET', body, prefix = '/admin' } = {}) {
  const auth = useAuthStore()
  const response = await fetch(`${baseUrl}/api${prefix}${path}`, {
    method,
    headers: {
      Authorization: `Bearer ${auth.token}`,
      ...(body ? { 'Content-Type': 'application/json' } : {}),
    },
    ...(body ? { body: JSON.stringify(body) } : {}),
  })
  if (response.status === 401) {
    auth.clearAuth()
    throw new Error('Votre session a expiré. Veuillez vous reconnecter.')
  }
  if (response.status === 403) {
    await auth.fetchUser().catch(() => {})
    throw new Error('Vous ne disposez plus des permissions nécessaires.')
  }
  const data = await response.json()
  if (!response.ok || data.success === false) {
    throw new Error(data.error || 'Impossible de réaliser cette opération.')
  }
  return data
}
