import sys

# Helper function to count set bits, compatible with Python < 3.10
# For non-negative integers (which our masks are)
def count_set_bits(n):
    return bin(n).count('1')

# Using global memoization dictionaries; must be cleared per test case.
memo_prefix_ORs_global = {}
memo_unite_global = {}

def solve():
    line_for_N = sys.stdin.readline()
    N = int(line_for_N.strip())
    
    adj = [[] for _ in range(N)]
    if N > 0: # Edges only if N > 0 (problem states N >= 2)
        for _ in range(N - 1):
            line_for_edge = sys.stdin.readline()
            u, v = map(int, line_for_edge.strip().split())
            adj[u - 1].append(v - 1)
            adj[v - 1].append(u - 1)

    MOD = 998244353
    
    memo_dfs_dp = {} 

    N_BITS = N 

    memo_prefix_ORs_global.clear()
    def get_prefix_ORs(mask):
        if mask == 0: return 0
        # N_BITS is fixed per test case, so (mask) could be enough if N_BITS is not part of key
        # However, if N_BITS could change (e.g. different N in same global memo), include it.
        # For this problem structure, N_BITS is effectively constant within one solve() call.
        state_tuple = (mask, N_BITS) 
        if state_tuple in memo_prefix_ORs_global: return memo_prefix_ORs_global[state_tuple]
        
        res = 0
        current_OR_val = 0
        for i in range(N_BITS):
            if (mask >> i) & 1:
                current_OR_val = 1
            if current_OR_val:
                res |= (1 << i)
        memo_prefix_ORs_global[state_tuple] = res
        return res

    memo_unite_global.clear()
    def unite(s1, s2, k_cross):
        state_tuple = (s1, s2, k_cross, N_BITS)
        if state_tuple in memo_unite_global:
            return memo_unite_global[state_tuple]

        p_s1 = get_prefix_ORs(s1)
        p_s2 = get_prefix_ORs(s2)
        
        s_ab = (s1 & p_s2) | (s2 & p_s1)
        
        res_mask = 0
        if N_BITS == 0:
             memo_unite_global[state_tuple] = 0
             return 0

        if k_cross < N_BITS:
            mask_ge_k_cross = ((1 << (N_BITS - k_cross)) - 1) << k_cross
            res_mask = s_ab & mask_ge_k_cross
        
        if k_cross < N_BITS:
            mask_lt_k_cross = (1 << k_cross) - 1
            if s_ab & mask_lt_k_cross: 
                 res_mask |= (1 << k_cross)
        
        memo_unite_global[state_tuple] = res_mask
        return res_mask
    
    if N == 0: # Problem constraints N >= 2, but defensive
        print(0)
        return
        
    order = []
    q = [0] # Assuming 0 is a valid node index if N >= 1
    if N == 0: # Should not happen based on constraints
        # Handle N=0 case if necessary, though problem says N>=2
        # If N=0, dp_root would be empty, etc.
        # For N>=2, node 0 always exists.
        pass
    else: # N >= 1
        visited_dfs_order = [False] * N
        visited_dfs_order[0] = True
        parent_map = [-1] * N
        
        head = 0
        while head < len(q):
            curr = q[head]; head += 1
            order.append(curr)
            for neighbor in adj[curr]:
                if not visited_dfs_order[neighbor]:
                    visited_dfs_order[neighbor] = True
                    parent_map[neighbor] = curr
                    q.append(neighbor)

    for u_idx in range(N - 1, -1, -1):
        u = order[u_idx]
        dp_u = {}

        dp_u[(N, N)] = 1 
        dp_u[(0, N)] = 1 
        dp_u[(N, 0)] = 1 

        for v_child in adj[u]:
            if parent_map[u] == v_child:
                continue
            
            dp_v_child = memo_dfs_dp[v_child]
            new_dp_u = {} 

            for (a1, b1), m1_mask in dp_u.items():
                for (a2_child, b2_child), m2_mask in dp_v_child.items():
                    a2 = a2_child + 1 if a2_child < N else N
                    b2 = b2_child + 1 if b2_child < N else N
                    
                    cur_a = min(a1, a2)
                    cur_b = min(b1, b2)
                    
                    k_c = 0 
                    if N_BITS > 0:
                        if a1 < N and b2_child < N :
                            k_c = max(k_c, min(N_BITS - 1, a1 + b2_child + 1))
                        if b1 < N and a2_child < N :
                            k_c = max(k_c, min(N_BITS - 1, b1 + a2_child + 1))
                    
                    united_mask = unite(m1_mask, m2_mask, k_c)
                    
                    if united_mask != 0:
                        current_val = new_dp_u.get((cur_a, cur_b), 0)
                        new_dp_u[(cur_a, cur_b)] = current_val | united_mask
            dp_u = new_dp_u
        memo_dfs_dp[u] = dp_u
    
    # If N=0, order is empty, loop for u_idx won't run. dp_root would need careful handling.
    # But N>=2, so order[0] (root) exists and its DP is computed.
    dp_root = memo_dfs_dp[0] 
    
    f_values = [0] * N_BITS
    
    for D_coolness_thresh in range(N_BITS): 
        count_le_D = 0
        mask_le_D = (1 << (D_coolness_thresh + 1)) - 1
        for m_mask in dp_root.values():
            relevant_m_values = m_mask & mask_le_D
            # Use the helper function here
            count_le_D = (count_le_D + count_set_bits(relevant_m_values)) % MOD
        f_values[D_coolness_thresh] = count_le_D

    total_colorings = pow(3, N, MOD)
    
    term1 = ((N - 1) * total_colorings) % MOD
    
    ans = term1
    
    # Sum f(D) for D from 0 to N_BITS-2 (i.e., N-2)
    # N_BITS-1 is N-1. If N=2, N_BITS-1 = 1. range(1) means D=0.
    # If N=1 (not per constraints), N_BITS-1 = 0. range(0) is empty loop.
    for D_coolness_thresh in range(N_BITS - 1): 
        ans = (ans - f_values[D_coolness_thresh] + MOD) % MOD
        
    print(ans)

if __name__ == "__main__":
    line_for_num_tc = sys.stdin.readline()
    num_test_cases = int(line_for_num_tc.strip())
    for _ in range(num_test_cases):
        solve()