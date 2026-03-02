import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

describe('Input Component', () => {
  it('renders correctly', () => {
    render(<Input placeholder="Enter text" />)
    
    const input = screen.getByPlaceholderText('Enter text')
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute('type', 'text')
  })

  it('accepts different input types', () => {
    const { rerender } = render(<Input type="email" placeholder="Email" />)
    expect(screen.getByPlaceholderText('Email')).toHaveAttribute('type', 'email')

    rerender(<Input type="password" placeholder="Password" />)
    expect(screen.getByPlaceholderText('Password')).toHaveAttribute('type', 'password')

    rerender(<Input type="number" placeholder="Number" />)
    expect(screen.getByPlaceholderText('Number')).toHaveAttribute('type', 'number')
  })

  it('handles value changes', async () => {
    const handleChange = vi.fn()
    const user = userEvent.setup()
    
    render(<Input onChange={handleChange} placeholder="Test" />)
    
    const input = screen.getByPlaceholderText('Test')
    await user.type(input, 'hello')
    
    expect(handleChange).toHaveBeenCalled()
  })

  it('can be disabled', () => {
    render(<Input disabled placeholder="Disabled" />)
    
    expect(screen.getByPlaceholderText('Disabled')).toBeDisabled()
  })

  it('applies custom className', () => {
    render(<Input className="custom-input" placeholder="Custom" />)
    
    expect(screen.getByPlaceholderText('Custom')).toHaveClass('custom-input')
  })
})

describe('Label Component', () => {
  it('renders correctly', () => {
    render(<Label>Username</Label>)
    
    expect(screen.getByText('Username')).toBeInTheDocument()
  })

  it('associates with form control', () => {
    render(
      <div>
        <Label htmlFor="username">Username</Label>
        <Input id="username" />
      </div>
    )
    
    const label = screen.getByText('Username')
    expect(label).toHaveAttribute('for', 'username')
  })
})

describe('Form Integration', () => {
  it('works with label and input together', async () => {
    const user = userEvent.setup()
    
    render(
      <div>
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" placeholder="Enter email" />
      </div>
    )
    
    const input = screen.getByLabelText(/email/i)
    await user.type(input, 'test@example.com')
    
    expect(input).toHaveValue('test@example.com')
  })
})
