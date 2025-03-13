import matplotlib.pyplot as plt
import matplotlib.patches as patches

# A function to blend two hex colors and return the mixed color in hex
def blend_colors(color1, color2):
    # Convert hex to RGB
    r1, g1, b1 = [int(color1[i:i+2], 16) for i in (1, 3, 5)]
    r2, g2, b2 = [int(color2[i:i+2], 16) for i in (1, 3, 5)]
    
    # Blend the colors (average the RGB values)
    r = int((r1 + r2) / 2)
    g = int((g1 + g2) / 2)
    b = int((b1 + b2) / 2)
    
    # Convert the blended RGB back to hex
    return f'#{r:02x}{g:02x}{b:02x}'

# Function to handle the complex barvanje (mixing) process
def complex_barvanje(hex_colors):
    # Start with a white color (you can change this to any initial color)
    current_mix = '#ffffff'
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Make the figure full-screen
    mngr = plt.get_current_fig_manager()
    mngr.window.state('zoomed')  # Full screen
    
    # Display the current mixed color and keep the window open
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')  # Hide axes
    
    # Plot the initial mix (white by default)
    mix_rect = ax.add_patch(patches.Rectangle((0, 0), 1, 1, color=current_mix))
    
    while True:
        # Show the current mix color
        print(f"Current mixed color: {current_mix}")
        print("Available colors:", ', '.join(hex_colors))
        
        try:
            selected_index = int(input(f"Enter color index to add (1 to {len(hex_colors)}), or 0 to stop: "))
            if selected_index == 0:
                break  # Exit the loop if 0 is entered
            if 1 <= selected_index <= len(hex_colors):
                # Blend the selected color with the current mix
                current_mix = blend_colors(current_mix, hex_colors[selected_index - 1])
                
                # Update the displayed mixed color
                mix_rect.set_facecolor(current_mix)  # Update the color of the mix
                plt.draw()  # Redraw the plot to reflect the changes
                
            else:
                print("Invalid color index, please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

# Function to plot selected colors and blended result for 'simple' mode
def plot_colors(hex_colors, indices):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    # Define the spacing for the squares
    spacing = 0.2
    square_size = 0.1
    
    # Plot the selected color squares
    for i, idx in enumerate(indices):
        color = hex_colors[idx - 1]  # Adjust for 1-based index
        ax.add_patch(patches.Rectangle((i * (square_size + spacing), 0), square_size, square_size, color=color))
    
    # Blend the selected colors and plot the mixed color square
    blended_color = blend_colors(hex_colors[indices[0] - 1], hex_colors[indices[1] - 1])
    ax.add_patch(patches.Rectangle(((len(indices) + 0.5) * (square_size + spacing), 0), square_size, square_size, color=blended_color))
    
    # Hide axes and other elements
    ax.axis('off')
    ax.set_xlim(0, (len(indices) + 1) * (square_size + spacing))
    ax.set_ylim(0, square_size + 0.1)
    
    # Show the plot in full screen (without window being visible)
    mngr = plt.get_current_fig_manager()
    mngr.window.state('zoomed')  # Full screen
    plt.close(fig)  # Close the figure immediately to prevent display

# Main function to process the file
def process_file(file_path):
    # Read the file and process lines
    with open(file_path, 'r') as file:
        for line in file:
            if "barve" in line:
                # Extract the color part and check for 'simple' or 'complex' keyword
                parts = line.split(';')
                colors_part = parts[1].split('!')[1]
                colors = colors_part.split(',')
                
                if 'simple' in parts[0]:
                    # Ask for the number of inputs and check if the number matches
                    print(f"Available colors: {', '.join(colors)}")
                    num_inputs = len(colors)
                    selected_indices = []

                    for i in range(num_inputs):
                        while True:
                            try:
                                selected_index = int(input(f"Please select color {i+1} (between 1 and {num_inputs}): "))
                                if 1 <= selected_index <= num_inputs:
                                    selected_indices.append(selected_index)
                                    break
                                else:
                                    print(f"Please enter a number between 1 and {num_inputs}.")
                            except ValueError:
                                print("Invalid input. Please enter a valid number.")
                    
                    plot_colors(colors, selected_indices)
                elif 'complex' in parts[0]:
                    # Call the complex barvanje function to handle mixing
                    complex_barvanje(colors)
                else:
                    print("The line does not have 'simple' or 'complex' keywords.")
                break

# Run the script with the file path
process_file('D:\\izvedba.txt')
