class Solution:
    def numIslands(self, grid: list[list[str]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        seen = [[False] * cols for _ in range(rows)]
        count = 0
        directions = ((-1, 0), (0, 1), (1, 0), (0, -1))

        for row in range(rows):
            for col in range(cols):
                if grid[row][col] != "1" or seen[row][col]:
                    continue

                count += 1
                seen[row][col] = True
                stack = [(row, col)]

                while stack:
                    r, c = stack.pop()
                    for dr, dc in directions:
                        nr, nc = r + dr, c + dc
                        if (0 <= nr < rows and 0 <= nc < cols
                                and grid[nr][nc] == "1"
                                and not seen[nr][nc]):
                            seen[nr][nc] = True
                            stack.append((nr, nc))

        return count
