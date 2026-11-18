async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`/api${path}`, options)
  } catch {
    throw new Error('Cannot reach the app server. Check that python run.py is still running.')
  }
  const data = await response.json().catch(() => null)
  if (!response.ok) throw new Error(data?.detail || `Request failed (${response.status})`)
  return data
}

const send = (method, path, body) =>
  request(path, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body ?? {}) })

export const api = {
  get: (path) => request(path),
  post: (path, body) => send('POST', path, body),
  put: (path, body) => send('PUT', path, body),
  patch: (path, body) => send('PATCH', path, body),
  remove: (path) => request(path, { method: 'DELETE' }),
  upload: (file) => {
    const form = new FormData()
    form.append('file', file)
    return request('/resume/upload', { method: 'POST', body: form })
  },
}
