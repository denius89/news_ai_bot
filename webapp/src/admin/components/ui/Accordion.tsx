import { AnimatePresence, motion } from 'framer-motion';
import React, { useState } from 'react';

type AccordionProps = {
    title: React.ReactNode;
    children: React.ReactNode;
    defaultOpen?: boolean;
};

export function Accordion({ title, children, defaultOpen = false }: AccordionProps) {
    const [open, setOpen] = useState(defaultOpen);
    return (
        <div className="border rounded-lg">
            <button
                type="button"
                className="w-full text-left px-3 py-2 flex items-center justify-between hover:bg-muted/50"
                aria-expanded={open}
                onClick={() => setOpen((o) => !o)}
            >
                <div className="font-medium">{title}</div>
                <div className={`transition-transform ${open ? 'rotate-90' : ''}`}>›</div>
            </button>
            <AnimatePresence initial={false}>
                {open && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: 'easeOut' }}
                    >
                        <div className="px-3 py-2">{children}</div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
