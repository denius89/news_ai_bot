/**
 * AdminInput component
 * Unified input field with label and hint
 */

import React from 'react';

interface AdminInputProps {
    label: string;
    type?: 'text' | 'number' | 'email' | 'password' | 'url';
    value: string | number;
    onChange: (value: string | number) => void;
    placeholder?: string;
    hint?: string;
    min?: number;
    max?: number;
    step?: number;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

export function AdminInput({
    label,
    type = 'text',
    value,
    onChange,
    placeholder,
    hint,
    min,
    max,
    step,
    required = false,
    disabled = false,
    className = '',
}: AdminInputProps) {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const newValue = type === 'number' ? parseFloat(e.target.value) || 0 : e.target.value;
        onChange(newValue);
    };

    return (
        <div className={className}>
            <label className="block text-sm font-medium mb-2 text-text">
                {label}
                {required && <span className="text-error ml-1">*</span>}
            </label>
            <input
                type={type}
                value={value}
                onChange={handleChange}
                placeholder={placeholder}
                min={min}
                max={max}
                step={step}
                required={required}
                disabled={disabled}
                className="input w-full"
            />
            {hint && (
                <p className="text-xs text-muted mt-1">{hint}</p>
            )}
        </div>
    );
}
