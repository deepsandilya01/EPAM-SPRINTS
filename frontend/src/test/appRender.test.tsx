import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from 'react-router-dom'
import { store } from '@/store'
import App from '@/App'

describe('Full App Rendering Smoke Test', () => {
  it('renders the application on root and graph-explorer without errors', async () => {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    const { container } = render(
      <Provider store={store}>
        <QueryClientProvider client={queryClient}>
          <MemoryRouter initialEntries={['/graph-explorer']}>
            <App />
          </MemoryRouter>
        </QueryClientProvider>
      </Provider>
    )

    // Verify main headings are in document after async query resolves
    expect(await screen.findByText(/Downstream trace from SUP-01/i)).toBeInTheDocument()
    expect(screen.getByText(/Input Parameters/i)).toBeInTheDocument()
    expect(screen.getByText(/Generate Graph/i)).toBeInTheDocument()
    expect(screen.getByText(/Traversal Performance/i)).toBeInTheDocument()
  })
})
