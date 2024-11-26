''' This help bot will take excel files as input, removes duplicate rows, fills N/A values. It then gives the detailed summary of your sheet. You can also create
7 basic visuals like bar graph, heatmap,etc., with it.'''

from excel_processor import ExcelProcessor
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

console = Console()

def print_header(text):
    """Print formatted header"""
    console.print(f"\n[bold blue]{text}[/bold blue]")
    console.print("-" * 50)

def print_summary(summary):
    """Print formatted summary"""
    print_header("Data Summary")

    # Basic Info
    basic_info = summary['Basic Info']
    console.print(Panel(
        "\n".join([
            f"Original Rows: {basic_info['Original_Rows']}",
            f"Original Columns: {basic_info['Original_Columns']}",
            f"Current Rows: {basic_info['Current_Rows']}",
            f"Current Columns: {basic_info['Current_Columns']}",
            f"Rows Removed: {basic_info['Rows_Removed']}",
            f"Columns: {', '.join(basic_info['Columns'])}"
        ]),
        title="Basic Information"
    ))

    # Data Types
    table = Table(title="Column Data Types")
    table.add_column("Column", style="cyan")
    table.add_column("Type", style="green")
    for col, dtype in summary['Data Types'].items():
        table.add_row(str(col), str(dtype))
    console.print(table)

    # Missing Values
    table = Table(title="Missing Values")
    table.add_column("Column", style="cyan")
    table.add_column("Missing Count", style="yellow")
    for col, count in summary['Missing Values'].items():
        table.add_row(str(col), str(count))
    console.print(table)

    # Numeric Summary
    if summary['Numeric Summary']:
        print_header("Numeric Columns Summary")
        for col, stats in summary['Numeric Summary'].items():
            console.print(f"\n[cyan]{col}[/cyan]")
            for stat, value in stats.items():
                console.print(f"{stat}: {value:.2f}")

    # Categorical Summary
    if summary['Categorical Summary']:
        print_header("Categorical Columns Summary")
        for col, stats in summary['Categorical Summary'].items():
            console.print(f"\n[cyan]{col}[/cyan]")
            console.print(f"Unique Values: {stats['unique_values']}")
            console.print("Top 5 Values:")
            for value, count in stats['top_5_values'].items():
                console.print(f"  {value}: {count}")

def create_visualization_menu(processor):
    """Interactive menu for creating visualizations"""
    print_header("Data Visualization")
    
    # Get plottable columns
    columns = processor.get_plottable_columns()
    
    # Show available columns
    console.print("\n[cyan]Available Numeric Columns:[/cyan]")
    for col in columns['numeric']:
        console.print(f"  • {col}")
    
    console.print("\n[cyan]Available Categorical Columns:[/cyan]")
    for col in columns['categorical']:
        console.print(f"  • {col}")
    
    # Show available plot types
    plot_types = {
        '1': ('scatter', 'Scatter Plot (requires 2 numeric columns)'),
        '2': ('bar', 'Bar Plot'),
        '3': ('line', 'Line Plot (requires 2 numeric columns)'),
        '4': ('histogram', 'Histogram (requires 1 numeric column)'),
        '5': ('box', 'Box Plot (requires 1 numeric column)'),
        '6': ('heatmap', 'Correlation Heatmap (uses all numeric columns)'),
        '7': ('pie', 'Pie Chart (best for categorical columns)')
    }
    
    console.print("\n[cyan]Available Plot Types:[/cyan]")
    for key, (_, desc) in plot_types.items():
        console.print(f"  {key}. {desc}")
    
    # Get user input
    plot_choice = Prompt.ask("\nSelect plot type", choices=[str(i) for i in range(1, 8)])
    plot_type = plot_types[plot_choice][0]
    
    # Get column selections based on plot type
    x_col = None
    y_col = None
    
    if plot_type == 'heatmap':
        pass  # No column selection needed
    elif plot_type in ['scatter', 'line']:
        x_col = Prompt.ask("Select first numeric column", choices=columns['numeric'])
        y_col = Prompt.ask("Select second numeric column", choices=columns['numeric'])
    elif plot_type in ['histogram', 'box']:
        x_col = Prompt.ask("Select numeric column", choices=columns['numeric'])
    elif plot_type in ['bar', 'pie']:
        x_col = Prompt.ask("Select column", choices=columns['numeric'] + columns['categorical'])
        if Confirm.ask("Include a numeric column for values?"):
            y_col = Prompt.ask("Select numeric column", choices=columns['numeric'])
    
    # Create visualization
    title = Prompt.ask("Enter plot title (optional)", default=None)
    
    with console.status("[bold green]Creating visualization..."):
        plot_path = processor.create_visualization(plot_type, x_col, y_col, title)
    
    if plot_path:
        console.print(f"\n[green]✓ Plot saved as: {plot_path}[/green]")
    else:
        console.print("\n[red]× Failed to create visualization[/red]")

def main():
    try:
        console.print("[bold blue]Excel Data Processor[/bold blue]", justify="center")
        console.print("=" * 50, justify="center")

        # Get file path
        file_path = input("\nEnter Excel file path: ").strip('"')
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Initialize processor
        with console.status("[bold green]Loading file..."):
            processor = ExcelProcessor(file_path)

        # Process file
        with console.status("[bold green]Processing data..."):
            processor.clean_data()
            processor.handle_duplicates()

        # Generate and display summary
        with console.status("[bold green]Generating summary..."):
            summary = processor.generate_summary()
            if summary:
                print_summary(summary)

        # Visualization menu
        while Confirm.ask("\nWould you like to create a visualization?"):
            create_visualization_menu(processor)

        # Save processed file
        with console.status("[bold green]Saving processed file..."):
            processor.save_processed_file()

        console.print("\n[bold green]✓ Processing completed successfully![/bold green]")

    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")

if __name__ == "__main__":
    main()
