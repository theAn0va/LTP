a = [1, 2, 3, 4, 5, 6]          # gerold
b = [1, 2, 3, 5, 5, 6]         # gertext mit geänderter Zeile, active_line = 3 
b = [1, 2, 4, 5, 6]            # gertext mit gelöschter Zeile, active_line = None
b1 = [1, 2, 3, 4, 5, 6, 7]      # gertext mit neuer Zeile, active_line = 6

if len(b1) == len(a):
    for i in range(0, len(a), 1):
        if a[i] != b1[i]:
            active_line = i


elif len(b1) < len(a):
    active_line = None

elif len(b1) > len(a):
    active_line = -1

print(active_line)