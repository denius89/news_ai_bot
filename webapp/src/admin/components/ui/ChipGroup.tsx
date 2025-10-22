import { useMemo, useState } from 'react';
import { Chip } from './Chip';

type ChipGroupProps = {
    items: string[];
    selected: string[];
    onChange: (next: string[]) => void;
    searchable?: boolean;
    className?: string;
};

export function ChipGroup({ items, selected, onChange, searchable = true, className = '' }: ChipGroupProps) {
    const [query, setQuery] = useState('');

    const filtered = useMemo(() => {
        const q = query.trim().toLowerCase();
        if (!q) return items;
        return items.filter((i) => i.toLowerCase().includes(q));
    }, [items, query]);

    const toggle = (value: string) => {
        const set = new Set(selected);
        if (set.has(value)) set.delete(value); else set.add(value);
        onChange(Array.from(set));
    };

    return (
        <div className={className}>
            {searchable && (
                <input
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Поиск"
                    className="input w-full mb-2"
                />
            )}
            <div className="flex flex-wrap gap-2">
                {filtered.map((item) => (
                    <Chip key={item} active={selected.includes(item)} onClick={() => toggle(item)} size="sm">
                        {item}
                    </Chip>
                ))}
            </div>
        </div>
    );
}
