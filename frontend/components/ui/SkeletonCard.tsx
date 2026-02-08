import * as React from 'react';
import { cn } from '@/lib/utils';

/**
 * T048: SkeletonCard Component
 * Loading state with sophisticated shimmer animation
 *
 * Zero third-party libraries - uses only Tailwind CSS utilities and native CSS animations
 */

/**
 * SkeletonCard component props
 */
export interface SkeletonCardProps {
  className?: string;
}

/**
 * SkeletonCard component
 *
 * @example
 * ```tsx
 * <SkeletonCard />
 * ```
 *
 * @example
 * ```tsx
 * <div className="space-y-4">
 *   {Array.from({ length: 3 }).map((_, i) => (
 *     <SkeletonCard key={i} />
 *   ))}
 * </div>
 * ```
 */
const SkeletonCard = ({ className }: SkeletonCardProps) => {
  return (
    <div
      className={cn(
        /**
         * T048: SkeletonCard visual specifications from design-system.md
         */
        'card bg-white p-6 h-32 dark:bg-slate-800',
        'border border-slate-100 dark:border-slate-700',
        className
      )}
    >
      <div className="space-y-4">
        {/* Title shimmer */}
        <div
          className={cn(
            'h-6 w-3/4 rounded-lg',
            /**
             * T048: Shimmer animation (1.5s infinite)
             * From design-system.md with gradient background
             */
            'bg-slate-100 dark:bg-slate-700',
            'animate-shimmer'
          )}
        />

        {/* Text shimmer */}
        <div
          className={cn(
            'h-4 w-1/2 rounded-lg',
            'bg-slate-100 dark:bg-slate-700',
            'animate-shimmer animate-delay-100'
          )}
        />

        {/* Text shimmer 2 */}
        <div
          className={cn(
            'h-4 w-2/3 rounded-lg',
            'bg-slate-100 dark:bg-slate-700',
            'animate-shimmer animate-delay-200'
          )}
        />
      </div>
    </div>
  );
};

export { SkeletonCard };
