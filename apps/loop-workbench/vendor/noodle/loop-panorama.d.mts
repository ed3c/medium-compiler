export function mountPanorama(root: HTMLElement, options: {
 graph: unknown;
 runs: unknown[];
 runIds?: string[] | null;
 goal?: string;
 onScope: (scope: {goal: string; runIds: string[] | null}) => void;
 onSelect: (value: unknown) => void;
 onFocus: (value: unknown) => void;
 onReset: () => void;
 readArtifact: (id: string) => Promise<string>;
 onReviewSelection?: undefined;
}): unknown;
