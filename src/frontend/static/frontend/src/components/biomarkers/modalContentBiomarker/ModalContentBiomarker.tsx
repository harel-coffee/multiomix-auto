import React from 'react'
import { Grid } from 'semantic-ui-react'
import { NameOfCGDSDataset } from '../../../utils/interfaces'
import { BiomarkerType, FormBiomarkerData, MoleculesSectionData, MoleculesTypeOfSelection } from '../types'
import { NewBiomarkerForm } from './NewBiomarkerForm/NewBiomarkerForm'
import './modalContentBiomarkerStyles.css'
import { MoleculeSection } from './moleculeSection/MoleculeSection'
interface ModalContentBiomarkerProps {
    biomarkerForm: FormBiomarkerData,
    handleFormChanges: (name: string, value) => void,
    handleKeyDown: (e) => void,
    addCGDSDataset: (datasetName: NameOfCGDSDataset) => void,
    removeCGDSDataset: (datasetName: NameOfCGDSDataset) => void,
    handleFormDatasetChanges: (datasetName: NameOfCGDSDataset, name: string, value: any) => void,
    addSurvivalFormTuple: (datasetName: NameOfCGDSDataset) => void,
    removeSurvivalFormTuple: (datasetName: NameOfCGDSDataset, idxSurvivalTuple: number) => void,
    handleSurvivalFormDatasetChanges: (datasetName: NameOfCGDSDataset, idx: number, name: string, value: any) => void,
    cleanForm: () => void,
    isFormEmpty: () => boolean,
    addingOrEditingCGDSStudy: boolean,
    canAddCGDSStudy: () => boolean,
    addOrEditStudy: () => void,
    handleChangeMoleculeSelected: (value: BiomarkerType) => void,
    handleChangeMoleculeInputSelected: (value: MoleculesTypeOfSelection) => void,
    handleAddMoleculeToSection: (value: MoleculesSectionData) => void,
    handleRemoveMolecule: (section: BiomarkerType, molecule: MoleculesSectionData) => void,
    handleGenesSymbolsFinder: (query: string) => void,
    handleGenesSymbols: (genes: string[]) => void,
    handleSelectOptionMolecule: (mol: MoleculesSectionData, section: BiomarkerType, itemSelected: string) => void,
}

export const ModalContentBiomarker = (props: ModalContentBiomarkerProps) => {
    return (
        <Grid columns={2} padded stackable divided className='biomarkers--modal--container'>
            <Grid.Column width={4} textAlign='left'>
                <NewBiomarkerForm
                    biomarkerForm={props.biomarkerForm}
                    handleFormChanges={props.handleFormChanges}
                    handleKeyDown={props.handleKeyDown}
                    addCGDSDataset={/* this.addCGDSDataset () => {} */() => { }}
                    removeCGDSDataset={/* this.removeCGDSDataset () => {} */() => { }}
                    handleFormDatasetChanges={props.handleFormDatasetChanges}
                    addSurvivalFormTuple={props.addSurvivalFormTuple}
                    removeSurvivalFormTuple={props.removeSurvivalFormTuple}
                    handleSurvivalFormDatasetChanges={props.handleSurvivalFormDatasetChanges}
                    cleanForm={props.cleanForm}
                    isFormEmpty={props.isFormEmpty}
                    addingOrEditingCGDSStudy={true}
                    canAddCGDSStudy={() => true}
                    addOrEditStudy={() => { }}
                    handleChangeMoleculeSelected={props.handleChangeMoleculeSelected}
                    handleChangeMoleculeInputSelected={props.handleChangeMoleculeInputSelected}
                    handleAddMoleculeToSection={props.handleAddMoleculeToSection}
                    handleGenesSymbolsFinder={props.handleGenesSymbolsFinder}
                    handleGenesSymbols={props.handleGenesSymbols}
                />
            </Grid.Column>
            <Grid.Column width={12}>
                <Grid columns={2} stackable className='biomarkers--modal--container'>
                    {Object.values(BiomarkerType).map(item => (
                        <MoleculeSection
                            key={item}
                            title={item}
                            biomarkerFormData={props.biomarkerForm.moleculesSection[item]}
                            handleRemoveMolecule={props.handleRemoveMolecule}
                            handleSelectOptionMolecule={props.handleSelectOptionMolecule}
                        />
                    ))}
                </Grid>
            </Grid.Column>
        </Grid >
    )
}
