full_block = VGroup(inner_block, algebra_eq)
full_block.arrange(DOWN, buff=0.45, aligned_edge=LEFT)

layout_why = VGroup(badge_why, full_block)
layout_why.arrange(DOWN, buff=0.5, aligned_edge=LEFT)
layout_why.to_edge(LEFT, buff=1.0)
layout_why.shift(UP * 0.2)