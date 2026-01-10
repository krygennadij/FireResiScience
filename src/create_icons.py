
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os

def create_icon(sides, filename):
    fig, ax = plt.subplots(figsize=(2, 2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Draw I-beam profile (schematic)
    # Flanges
    ax.add_patch(patches.Rectangle((2, 8), 6, 1, facecolor='gray', edgecolor='black'))
    ax.add_patch(patches.Rectangle((2, 1), 6, 1, facecolor='gray', edgecolor='black'))
    # Web
    ax.add_patch(patches.Rectangle((4.5, 2), 1, 6, facecolor='gray', edgecolor='black'))
    
    # Draw Arrows (Fire)
    style = "Simple, tail_width=2, head_width=8, head_length=8"
    kw = dict(arrowstyle=style, color="red")
    
    # Bottom
    ax.add_patch(patches.FancyArrowPatch((5, 0), (5, 1), **kw))
    
    # Left
    ax.add_patch(patches.FancyArrowPatch((0, 5), (2, 5), **kw))
    
    # Right
    ax.add_patch(patches.FancyArrowPatch((10, 5), (8, 5), **kw))
    
    # Top (only for 4 sides)
    if sides == 4:
        ax.add_patch(patches.FancyArrowPatch((5, 10), (5, 9), **kw))
        
    plt.savefig(filename, transparent=True, dpi=100)
    plt.close()

if __name__ == "__main__":
    assets_dir = "assets"
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir)
        
    create_icon(4, os.path.join(assets_dir, "icon_4_sides.png"))
    create_icon(3, os.path.join(assets_dir, "icon_3_sides.png"))
    print("Icons created.")
