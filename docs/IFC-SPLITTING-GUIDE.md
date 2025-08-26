# IFC File Splitting and Filtering Guide

## Overview

Based on research into IFC manipulation libraries and tools, there are several proven approaches for programmatically splitting large IFC files into smaller, manageable parts by removing unrelated elements and non-essential data.

## Primary Approaches

### 1. IfcOpenShell-Based Splitting (Recommended)

**Installation:**
```bash
pip install ifcopenshell
```

**Spatial-Based Splitting (By Building Levels):**
```python
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector

def split_ifc_by_levels(input_file, output_dir):
    """Split IFC file by building storeys"""
    model = ifcopenshell.open(input_file)
    
    # Get all building storeys
    storeys = model.by_type('IfcBuildingStorey')
    
    for storey in storeys:
        # Create new IFC file for this level
        new_model = ifcopenshell.file(schema=model.schema)
        
        # Copy project structure
        project = model.by_type('IfcProject')[0]
        site = model.by_type('IfcSite')[0] if model.by_type('IfcSite') else None
        building = model.by_type('IfcBuilding')[0] if model.by_type('IfcBuilding') else None
        
        # Add essential project elements
        new_model.add(project)
        if site:
            new_model.add(site)
        if building:
            new_model.add(building)
        new_model.add(storey)
        
        # Get all elements contained in this storey
        level_elements = ifcopenshell.util.selector.filter_elements(
            model, f'IfcElement, location="{storey.Name}"'
        )
        
        # Add all elements and their dependencies
        for element in level_elements:
            new_model.add(element)
            # Add related elements (type, properties, etc.)
            for related in model.traverse(element):
                new_model.add(related)
        
        # Save level-specific file
        output_file = f"{output_dir}/{storey.Name.replace(' ', '_')}.ifc"
        new_model.write(output_file)
        print(f"Created: {output_file}")

# Usage
split_ifc_by_levels("large_building.ifc", "output_levels/")
```

**Functional-Based Splitting (By Discipline):**
```python
def split_ifc_by_discipline(input_file, output_dir):
    """Split IFC file by building disciplines (Architecture, Structure, MEP)"""
    model = ifcopenshell.open(input_file)
    
    disciplines = {
        'Architecture': [
            'IfcWall', 'IfcWindow', 'IfcDoor', 'IfcSlab', 'IfcRoof', 
            'IfcStair', 'IfcRailing', 'IfcCurtainWall', 'IfcSpace'
        ],
        'Structure': [
            'IfcBeam', 'IfcColumn', 'IfcFooting', 'IfcPile', 
            'IfcReinforcingBar', 'IfcReinforcingMesh'
        ],
        'MEP': [
            'IfcPipeSegment', 'IfcDuctSegment', 'IfcFlowTerminal',
            'IfcFlowFitting', 'IfcFlowController', 'IfcEnergyConversionDevice',
            'IfcDistributionElement', 'IfcElectricAppliance'
        ]
    }
    
    for discipline, element_types in disciplines.items():
        new_model = ifcopenshell.file(schema=model.schema)
        
        # Copy project structure
        project = model.by_type('IfcProject')[0]
        new_model.add(project)
        
        # Copy spatial structure
        for spatial_type in ['IfcSite', 'IfcBuilding', 'IfcBuildingStorey']:
            for element in model.by_type(spatial_type):
                new_model.add(element)
        
        # Add discipline-specific elements
        for element_type in element_types:
            elements = model.by_type(element_type)
            for element in elements:
                new_model.add(element)
                # Add dependencies
                for related in model.traverse(element):
                    new_model.add(related)
        
        output_file = f"{output_dir}/{discipline}.ifc"
        new_model.write(output_file)
        print(f"Created {discipline}: {output_file}")

# Usage
split_ifc_by_discipline("large_building.ifc", "output_disciplines/")
```

**Advanced Filtering (Remove Non-Essential Data):**
```python
def clean_ifc_file(input_file, output_file, filters=None):
    """Remove non-essential elements to reduce file size"""
    model = ifcopenshell.open(input_file)
    
    default_filters = {
        'remove_annotations': True,
        'remove_grids': True,
        'remove_spaces': False,  # Keep spaces for spatial queries
        'remove_openings': False,  # Keep for geometry accuracy
        'simplify_properties': True,
        'remove_materials': False,
        'remove_geometry_details': False
    }
    
    if filters:
        default_filters.update(filters)
    
    elements_to_remove = []
    
    # Remove annotations
    if default_filters['remove_annotations']:
        elements_to_remove.extend(model.by_type('IfcAnnotation'))
    
    # Remove grids
    if default_filters['remove_grids']:
        elements_to_remove.extend(model.by_type('IfcGrid'))
        elements_to_remove.extend(model.by_type('IfcGridAxis'))
    
    # Remove spaces (if not needed for analysis)
    if default_filters['remove_spaces']:
        elements_to_remove.extend(model.by_type('IfcSpace'))
    
    # Remove elements
    for element in elements_to_remove:
        try:
            model.remove(element)
        except:
            pass  # Element might already be removed due to dependencies
    
    # Simplify properties (remove redundant property sets)
    if default_filters['simplify_properties']:
        redundant_psets = []
        for pset in model.by_type('IfcPropertySet'):
            # Remove empty property sets
            if not pset.HasProperties:
                redundant_psets.append(pset)
            # Remove duplicate property sets (same name, same owner)
            # Implementation would check for duplicates
        
        for pset in redundant_psets:
            try:
                model.remove(pset)
            except:
                pass
    
    model.write(output_file)
    
    # Calculate size reduction
    import os
    original_size = os.path.getsize(input_file) / (1024 * 1024)  # MB
    new_size = os.path.getsize(output_file) / (1024 * 1024)  # MB
    reduction = ((original_size - new_size) / original_size) * 100
    
    print(f"Original: {original_size:.2f} MB")
    print(f"Cleaned: {new_size:.2f} MB")
    print(f"Reduction: {reduction:.1f}%")

# Usage
clean_ifc_file("large_file.ifc", "cleaned_file.ifc", {
    'remove_annotations': True,
    'remove_grids': True,
    'simplify_properties': True
})
```

### 2. Spatial Zone-Based Splitting

```python
def split_by_spatial_zones(input_file, output_dir, zone_criteria):
    """Split by custom spatial criteria (e.g., wings, zones, areas)"""
    model = ifcopenshell.open(input_file)
    
    # Define zones by spatial bounds or naming patterns
    zones = {
        'North_Wing': 'location=/.*North.*/',
        'South_Wing': 'location=/.*South.*/',
        'East_Wing': 'location=/.*East.*/',
        'West_Wing': 'location=/.*West.*/',
        'Core': 'location=/.*Core.*/'
    }
    
    for zone_name, zone_filter in zones.items():
        new_model = ifcopenshell.file(schema=model.schema)
        
        # Copy project structure
        for element in model.by_type('IfcProject'):
            new_model.add(element)
        
        # Filter elements by zone
        zone_elements = ifcopenshell.util.selector.filter_elements(
            model, f'IfcElement, {zone_filter}'
        )
        
        if zone_elements:
            # Add spatial context for zone
            for spatial_element in zone_elements:
                container = ifcopenshell.util.element.get_container(spatial_element)
                if container:
                    new_model.add(container)
            
            # Add zone elements and dependencies
            for element in zone_elements:
                new_model.add(element)
                for related in model.traverse(element, max_levels=2):
                    new_model.add(related)
            
            output_file = f"{output_dir}/{zone_name}.ifc"
            new_model.write(output_file)
            print(f"Created zone {zone_name}: {output_file} ({len(zone_elements)} elements)")

# Usage
split_by_spatial_zones("large_building.ifc", "output_zones/", {})
```

### 3. Geometric Complexity-Based Filtering

```python
def filter_by_geometric_complexity(input_file, output_file, max_vertices=10000):
    """Remove overly complex geometric elements"""
    model = ifcopenshell.open(input_file)
    
    import ifcopenshell.geom
    
    # Configure geometry settings
    settings = ifcopenshell.geom.settings()
    settings.set(settings.USE_WORLD_COORDS, True)
    
    complex_elements = []
    
    for element in model.by_type('IfcProduct'):
        if element.Representation:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                vertex_count = len(shape.geometry.verts) // 3  # verts are x,y,z
                
                if vertex_count > max_vertices:
                    complex_elements.append(element)
                    print(f"Removing complex element {element.GlobalId}: {vertex_count} vertices")
                    
            except:
                # Skip elements that can't generate geometry
                continue
    
    # Remove overly complex elements
    for element in complex_elements:
        try:
            model.remove(element)
        except:
            pass
    
    model.write(output_file)
    print(f"Removed {len(complex_elements)} complex elements")

# Usage
filter_by_geometric_complexity("complex_model.ifc", "simplified_model.ifc", max_vertices=5000)
```

### 4. Property-Based Filtering

```python
def filter_by_properties(input_file, output_file, property_filters):
    """Filter elements based on property values"""
    model = ifcopenshell.open(input_file)
    
    # Example property filters
    # property_filters = {
    #     'fire_rating_only': {'filter': 'IfcElement, /Pset_.*Common/.FireRating != NULL'},
    #     'load_bearing_only': {'filter': 'IfcElement, /Pset_.*Common/.LoadBearing=TRUE'},
    #     'exclude_temp_elements': {'filter': 'IfcElement, ! /Pset_.*Common/.Status=TEMPORARY'}
    # }
    
    filtered_elements = set()
    
    for filter_name, filter_config in property_filters.items():
        elements = ifcopenshell.util.selector.filter_elements(
            model, filter_config['filter']
        )
        filtered_elements.update(elements)
        print(f"Filter '{filter_name}': {len(elements)} elements")
    
    # Create new model with filtered elements
    new_model = ifcopenshell.file(schema=model.schema)
    
    # Copy project structure
    for element in model.by_type('IfcProject'):
        new_model.add(element)
    
    # Add spatial structure
    spatial_elements = model.by_type('IfcSpatialStructureElement')
    for element in spatial_elements:
        new_model.add(element)
    
    # Add filtered elements and dependencies
    for element in filtered_elements:
        new_model.add(element)
        for related in model.traverse(element):
            new_model.add(related)
    
    new_model.write(output_file)
    print(f"Created filtered model with {len(filtered_elements)} elements")

# Usage
property_filters = {
    'structural_only': {
        'filter': 'IfcBeam, IfcColumn, IfcWall, /Pset_.*Common/.LoadBearing=TRUE'
    },
    'fire_rated_only': {
        'filter': 'IfcElement, /Pset_.*Common/.FireRating != NULL'
    }
}
filter_by_properties("building.ifc", "filtered_building.ifc", property_filters)
```

### 5. Complete Splitting Workflow

```python
def comprehensive_ifc_splitter(input_file, output_dir):
    """Complete workflow for splitting large IFC files"""
    import os
    import shutil
    
    os.makedirs(output_dir, exist_ok=True)
    
    model = ifcopenshell.open(input_file)
    original_size = os.path.getsize(input_file) / (1024 * 1024)
    
    print(f"Processing: {input_file} ({original_size:.2f} MB)")
    print(f"Schema: {model.schema}")
    print(f"Total elements: {len(model.by_type('IfcProduct'))}")
    
    # 1. Clean and optimize
    cleaned_file = f"{output_dir}/cleaned_base.ifc"
    clean_ifc_file(input_file, cleaned_file, {
        'remove_annotations': True,
        'remove_grids': True,
        'simplify_properties': True
    })
    
    # 2. Split by levels
    levels_dir = f"{output_dir}/levels"
    os.makedirs(levels_dir, exist_ok=True)
    split_ifc_by_levels(cleaned_file, levels_dir)
    
    # 3. Split by disciplines
    disciplines_dir = f"{output_dir}/disciplines"
    os.makedirs(disciplines_dir, exist_ok=True)
    split_ifc_by_discipline(cleaned_file, disciplines_dir)
    
    # 4. Create summary
    summary = {
        'original_file': input_file,
        'original_size_mb': original_size,
        'cleaned_size_mb': os.path.getsize(cleaned_file) / (1024 * 1024),
        'output_files': []
    }
    
    for root, dirs, files in os.walk(output_dir):
        for file in files:
            if file.endswith('.ifc'):
                filepath = os.path.join(root, file)
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                summary['output_files'].append({
                    'name': file,
                    'path': filepath,
                    'size_mb': size_mb
                })
    
    print(f"\\nSplitting complete!")
    print(f"Original: {summary['original_size_mb']:.2f} MB")
    print(f"Cleaned base: {summary['cleaned_size_mb']:.2f} MB")
    print(f"Generated {len(summary['output_files'])} split files")
    
    return summary

# Usage
summary = comprehensive_ifc_splitter("B142-KCX-ZZ-ZZ-M-X-0001.ifc", "split_output/")
```

## Integration with Current Workflow

To integrate with your existing fragment conversion system:

```python
def split_and_convert_workflow(large_ifc_file, output_fragments_dir):
    """Split large IFC and convert parts to fragments"""
    
    # 1. Split the large file
    split_dir = "temp_split"
    summary = comprehensive_ifc_splitter(large_ifc_file, split_dir)
    
    # 2. Convert each split file to fragments
    fragment_results = []
    
    for file_info in summary['output_files']:
        if file_info['size_mb'] < 500:  # Only convert manageable files
            ifc_path = file_info['path']
            frag_path = f"{output_fragments_dir}/{file_info['name'].replace('.ifc', '.frag')}"
            
            # Use your existing converter
            try:
                # Your fragment conversion code here
                result = convert_ifc_to_fragments(ifc_path, frag_path)
                fragment_results.append({
                    'ifc_file': file_info['name'],
                    'fragment_file': frag_path,
                    'success': result['success']
                })
            except Exception as e:
                print(f"Conversion failed for {file_info['name']}: {e}")
    
    # 3. Cleanup temporary files
    shutil.rmtree(split_dir)
    
    return fragment_results

# Usage for B142-KCX file
results = split_and_convert_workflow(
    "D:/XIF2/data/ifc/B142-KCX-ZZ-ZZ-M-X-0001.ifc",
    "D:/XIF2/data/fragments/B142-KCX-parts/"
)
```

## Key Benefits

1. **Memory Management**: Each split file is much smaller and fits within web-ifc limits
2. **Parallel Processing**: Multiple smaller files can be processed simultaneously
3. **Selective Loading**: Only load relevant building parts for specific views
4. **Error Isolation**: If one part fails, others still work
5. **Progressive Enhancement**: Load building shell first, then details

## Tools Required

- **IfcOpenShell**: `pip install ifcopenshell`
- **Python 3.8+**: For script execution
- **Sufficient Disk Space**: Split files temporarily require 2-3x original size

This approach should handle the B142-KCX file by breaking it into manageable 100-500MB chunks that can be successfully converted to fragments.
