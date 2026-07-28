import List 
class Solution:
    def countComponents(self, n: int, edges: List[List[int]]) -> int:
        par = [i for i in range(n) ]
        rank = [1]*n

        def find(n1):
            res = n1
            while res!= par[res]: ## until res' parent = itself -> means cannot reach further higher (assume root is the highest)
                par[res] = par[par[res]] ## optimize: path compression (halving) set res parents as its grant parent
                res = par[res]
            return res
        
        def union(n1,n2):
            p1, p2 = find(n1), find(n2)

            if p1 == p2:
                return 0
            
            if rank[p1] > rank[p2]:
                rank[p1] += rank[p2]
                par[p2] = p1
            
            else:
                rank[p2] += rank[p2]
                par[p1] = p2
            return 1
        
        res = n
        for n1, n2 in edges:
            ##if union(n1,n2):
                res-= union(n1,n2)
        
        return res


        