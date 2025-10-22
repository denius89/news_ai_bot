/**
 * AdminSelect component
 * Unified select field with label and hint
 */

import React from 'react';

interface AdminSelectOption {
    value: string | number;
    label: string;
}

interface AdminSelectProps {
    label: string;
    value: string | number;
    onChange: (value: string | number) => void;
    options: AdminSelectOption[];
    hint?: string;
    required?: boolean;
    disabled?: boolean;
    className?: string;
}

export function AdminSelect({
    label,
    value,
    onChange,
    options,
    hint,
    required = false,
    disabled = false,
    className = '',
}: AdminSelectProps) {
    const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        onChange(e.target.value);
    };

    return (
        <div className={className}>
            <label className="block text-sm font-medium mb-2 text-text">
                {label}
                {required && <span className="text-error ml-1">*</span>}
            </label>
            <select
                value={value}
                onChange={handleChange}
                required={required}
                disabled={disabled}
                className="input w-full"
            >
                {options.map((option) => (
                    <option key={option.value} value={option.value}>
                        {option.label}
                    </option>
                ))}
            </select>
            {hint && (
                <p className="text-xs text-muted mt-1">{hint}</p>
            )}
        </div>
    );
}
