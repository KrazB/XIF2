"""
IFC File Splitter - Practical implementation for large IFC files

This script provides a complete solution for splitting large IFC files into
manageable parts that can be processed by the fragments converter.

Usage:
    python ifc_splitter.py input.ifc output_directory [--method levels|disciplines|zones]
"""

import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.selector
import os
import sys
import argparse
import time
from pathlib import Path


class IfcFileSplitter:
    def __init__(self, input_file, output_dir):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Loading IFC file: {self.input_file}")
        self.model = ifcopenshell.open(str(self.input_file))
        
        # Get file statistics
        self.original_size = self.input_file.stat().st_size / (1024 * 1024)  # MB
        self.total_elements = len(self.model.by_type('IfcProduct'))
        
        print(f"Schema: {self.model.schema}")
        print(f"Size: {self.original_size:.2f} MB")
        print(f"Total elements: {self.total_elements:,}")
    
    def clean_model(self, remove_annotations=True, remove_grids=True, remove_projections=True):
        """Remove non-essential elements to reduce file size"""
        print("\n=== CLEANING MODEL ===")
        
        elements_to_remove = []
        removed_counts = {}
        
        if remove_annotations:
            annotations = self.model.by_type('IfcAnnotation')
            elements_to_remove.extend(annotations)
            removed_counts['Annotations'] = len(annotations)
        
        if remove_grids:
            grids = self.model.by_type('IfcGrid')
            grid_axes = self.model.by_type('IfcGridAxis')
            elements_to_remove.extend(grids + grid_axes)
            removed_counts['Grids'] = len(grids) + len(grid_axes)
        
        if remove_projections:
            projections = self.model.by_type('IfcProjectionElement')
            elements_to_remove.extend(projections)
            removed_counts['Projections'] = len(projections)
        
        # Remove elements
        total_removed = 0
        for element in elements_to_remove:
            try:
                self.model.remove(element)
                total_removed += 1
            except Exception as e:
                # Element might already be removed due to dependencies
                pass
        
        print(f"Removed {total_removed:,} elements:")
        for category, count in removed_counts.items():
            if count > 0:
                print(f"  {category}: {count:,}")
        
        return total_removed
    
    def split_by_building_storeys(self):
        """Split IFC file by building storeys/levels"""
        print("\n=== SPLITTING BY BUILDING STOREYS ===")
        
        storeys = self.model.by_type('IfcBuildingStorey')
        if not storeys:
            print("No building storeys found!")
            return []
        
        print(f"Found {len(storeys)} building storeys")
        
        split_files = []
        
        for storey in storeys:
            storey_name = storey.Name or f"Storey_{storey.id()}"
            safe_name = "".join(c for c in storey_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            
            print(f"\nProcessing storey: {storey_name}")
            
            # Create new model for this storey
            new_model = ifcopenshell.file(schema=self.model.schema)
            
            # Copy project structure
            project = self.model.by_type('IfcProject')[0]
            new_model.add(project)
            
            # Copy spatial hierarchy up to building
            sites = self.model.by_type('IfcSite')
            buildings = self.model.by_type('IfcBuilding')
            
            for site in sites:
                new_model.add(site)
            for building in buildings:
                new_model.add(building)
            
            # Add the storey
            new_model.add(storey)
            
            # Find all elements contained in this storey
            try:
                storey_elements = ifcopenshell.util.selector.filter_elements(
                    self.model, f'IfcElement, location="{storey_name}"'
                )
            except:
                # Fallback: find elements by spatial containment
                storey_elements = []
                for rel in self.model.by_type('IfcRelContainedInSpatialStructure'):
                    if rel.RelatingStructure == storey:
                        storey_elements.extend(rel.RelatedElements)
            
            print(f"  Found {len(storey_elements):,} elements in storey")
            
            if storey_elements:
                # Add elements and their dependencies
                added_count = 0
                for element in storey_elements:
                    try:
                        new_model.add(element)
                        added_count += 1
                        
                        # Add element type and properties
                        if hasattr(element, 'IsTypedBy') and element.IsTypedBy:
                            for rel in element.IsTypedBy:
                                if rel.RelatingType:
                                    new_model.add(rel.RelatingType)
                        
                        # Add property sets
                        if hasattr(element, 'IsDefinedBy') and element.IsDefinedBy:
                            for rel in element.IsDefinedBy:
                                new_model.add(rel)
                                if hasattr(rel, 'RelatingPropertyDefinition'):
                                    new_model.add(rel.RelatingPropertyDefinition)
                        
                    except Exception as e:
                        # Skip elements that can't be added
                        continue
                
                print(f"  Added {added_count:,} elements to new model")
                
                # Save storey file
                output_file = self.output_dir / f"{safe_name}.ifc"
                new_model.write(str(output_file))
                
                file_size = output_file.stat().st_size / (1024 * 1024)
                print(f"  Saved: {output_file.name} ({file_size:.2f} MB)")
                
                split_files.append({
                    'name': output_file.name,
                    'path': str(output_file),
                    'size_mb': file_size,
                    'elements': added_count,
                    'type': 'storey',
                    'original_name': storey_name
                })
        
        return split_files
    
    def split_by_disciplines(self):
        """Split IFC file by building disciplines"""
        print("\n=== SPLITTING BY DISCIPLINES ===")
        
        disciplines = {
            'Architecture': [
                'IfcWall', 'IfcWindow', 'IfcDoor', 'IfcSlab', 'IfcRoof', 
                'IfcStair', 'IfcRailing', 'IfcCurtainWall', 'IfcSpace',
                'IfcCovering', 'IfcFurnishingElement'
            ],
            'Structure': [
                'IfcBeam', 'IfcColumn', 'IfcFooting', 'IfcPile', 
                'IfcReinforcingBar', 'IfcReinforcingMesh', 'IfcMember',
                'IfcPlate', 'IfcTendon', 'IfcTendonAnchor'
            ],
            'MEP': [
                'IfcPipeSegment', 'IfcDuctSegment', 'IfcFlowTerminal',
                'IfcFlowFitting', 'IfcFlowController', 'IfcEnergyConversionDevice',
                'IfcDistributionElement', 'IfcElectricAppliance', 'IfcFlowMovingDevice',
                'IfcFlowStorageDevice', 'IfcFlowTreatmentDevice'
            ],
            'Equipment': [
                'IfcFurnishingElement', 'IfcSystemFurnitureElement',
                'IfcElectricAppliance', 'IfcFireSuppressionTerminal',
                'IfcSanitaryTerminal', 'IfcMedicalDevice'
            ]
        }
        
        split_files = []
        
        for discipline_name, element_types in disciplines.items():
            print(f"\nProcessing discipline: {discipline_name}")
            
            # Count elements in this discipline
            discipline_elements = []
            for element_type in element_types:
                elements = self.model.by_type(element_type)
                discipline_elements.extend(elements)
            
            if not discipline_elements:
                print(f"  No elements found for {discipline_name}")
                continue
            
            print(f"  Found {len(discipline_elements):,} elements")
            
            # Create new model
            new_model = ifcopenshell.file(schema=self.model.schema)
            
            # Copy project structure
            project = self.model.by_type('IfcProject')[0]
            new_model.add(project)
            
            # Copy spatial structure
            for spatial_type in ['IfcSite', 'IfcBuilding', 'IfcBuildingStorey', 'IfcSpace']:
                for element in self.model.by_type(spatial_type):
                    try:
                        new_model.add(element)
                    except:
                        pass
            
            # Add discipline elements
            added_count = 0
            for element in discipline_elements:
                try:
                    new_model.add(element)
                    added_count += 1
                    
                    # Add related elements (types, properties, materials)
                    for related in self.model.traverse(element, max_levels=2):
                        try:
                            new_model.add(related)
                        except:
                            pass
                            
                except Exception as e:
                    continue
            
            print(f"  Added {added_count:,} elements to new model")
            
            # Save discipline file
            output_file = self.output_dir / f"{discipline_name}.ifc"
            new_model.write(str(output_file))
            
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"  Saved: {output_file.name} ({file_size:.2f} MB)")
            
            split_files.append({
                'name': output_file.name,
                'path': str(output_file),
                'size_mb': file_size,
                'elements': added_count,
                'type': 'discipline',
                'original_name': discipline_name
            })
        
        return split_files
    
    def split_by_size_limit(self, max_elements=100000):
        """Split file into chunks based on element count"""
        print(f"\n=== SPLITTING BY SIZE LIMIT ({max_elements:,} elements per file) ===")
        
        all_elements = self.model.by_type('IfcProduct')
        total_elements = len(all_elements)
        num_chunks = (total_elements + max_elements - 1) // max_elements
        
        print(f"Total elements: {total_elements:,}")
        print(f"Will create {num_chunks} chunks")
        
        split_files = []
        
        for chunk_idx in range(num_chunks):
            start_idx = chunk_idx * max_elements
            end_idx = min(start_idx + max_elements, total_elements)
            chunk_elements = all_elements[start_idx:end_idx]
            
            print(f"\nProcessing chunk {chunk_idx + 1}/{num_chunks} ({len(chunk_elements):,} elements)")
            
            # Create new model
            new_model = ifcopenshell.file(schema=self.model.schema)
            
            # Copy project structure
            project = self.model.by_type('IfcProject')[0]
            new_model.add(project)
            
            # Copy spatial structure
            for spatial_type in ['IfcSite', 'IfcBuilding', 'IfcBuildingStorey']:
                for element in self.model.by_type(spatial_type):
                    try:
                        new_model.add(element)
                    except:
                        pass
            
            # Add chunk elements
            added_count = 0
            for element in chunk_elements:
                try:
                    new_model.add(element)
                    added_count += 1
                    
                    # Add essential dependencies only
                    if hasattr(element, 'IsTypedBy') and element.IsTypedBy:
                        for rel in element.IsTypedBy:
                            if rel.RelatingType:
                                try:
                                    new_model.add(rel.RelatingType)
                                except:
                                    pass
                                    
                except Exception as e:
                    continue
            
            # Save chunk file
            output_file = self.output_dir / f"chunk_{chunk_idx + 1:03d}.ifc"
            new_model.write(str(output_file))
            
            file_size = output_file.stat().st_size / (1024 * 1024)
            print(f"  Saved: {output_file.name} ({file_size:.2f} MB)")
            
            split_files.append({
                'name': output_file.name,
                'path': str(output_file),
                'size_mb': file_size,
                'elements': added_count,
                'type': 'chunk',
                'original_name': f"Chunk {chunk_idx + 1}"
            })
        
        return split_files
    
    def create_summary_report(self, split_files, method):
        """Create a summary report of the splitting operation"""
        print("\n=== SPLITTING SUMMARY ===")
        
        total_split_size = sum(f['size_mb'] for f in split_files)
        total_split_elements = sum(f['elements'] for f in split_files)
        
        print(f"Method: {method}")
        print(f"Original file: {self.original_size:.2f} MB, {self.total_elements:,} elements")
        print(f"Split into: {len(split_files)} files")
        print(f"Total split size: {total_split_size:.2f} MB")
        print(f"Total split elements: {total_split_elements:,}")
        
        print(f"\nSplit files:")
        for i, file_info in enumerate(split_files, 1):
            print(f"  {i:2d}. {file_info['name']:<30} {file_info['size_mb']:>8.2f} MB  {file_info['elements']:>8,} elements")
        
        # Save summary to file
        summary_file = self.output_dir / "splitting_summary.txt"
        with open(summary_file, 'w') as f:
            f.write(f"IFC File Splitting Summary\n")
            f.write(f"=========================\n\n")
            f.write(f"Original file: {self.input_file}\n")
            f.write(f"Original size: {self.original_size:.2f} MB\n")
            f.write(f"Original elements: {self.total_elements:,}\n")
            f.write(f"Splitting method: {method}\n")
            f.write(f"Split date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"Split files ({len(split_files)} total):\n")
            for file_info in split_files:
                f.write(f"  {file_info['name']}: {file_info['size_mb']:.2f} MB, {file_info['elements']:,} elements\n")
        
        print(f"\nSummary saved to: {summary_file}")
        return split_files


def main():
    parser = argparse.ArgumentParser(description="Split large IFC files into manageable parts")
    parser.add_argument("input_file", help="Input IFC file path")
    parser.add_argument("output_dir", help="Output directory for split files")
    parser.add_argument("--method", choices=['storeys', 'disciplines', 'chunks'], 
                       default='storeys', help="Splitting method (default: storeys)")
    parser.add_argument("--clean", action='store_true', 
                       help="Clean model before splitting (remove annotations, grids)")
    parser.add_argument("--max-elements", type=int, default=100000,
                       help="Maximum elements per chunk (for chunks method)")
    
    args = parser.parse_args()
    
    try:
        # Initialize splitter
        splitter = IfcFileSplitter(args.input_file, args.output_dir)
        
        # Clean model if requested
        if args.clean:
            splitter.clean_model()
        
        # Split based on method
        if args.method == 'storeys':
            split_files = splitter.split_by_building_storeys()
        elif args.method == 'disciplines':
            split_files = splitter.split_by_disciplines()
        elif args.method == 'chunks':
            split_files = splitter.split_by_size_limit(args.max_elements)
        
        # Create summary
        splitter.create_summary_report(split_files, args.method)
        
        print(f"\nSplitting complete! Output files in: {args.output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
