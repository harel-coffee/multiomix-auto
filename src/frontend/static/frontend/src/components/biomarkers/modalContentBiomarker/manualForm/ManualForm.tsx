import React from 'react'
import { Grid } from 'semantic-ui-react'
import { BiomarkerType, FormBiomarkerData, MoleculesSectionData, MoleculesTypeOfSelection } from './../../types'
import { NewBiomarkerForm } from './newBiomarkerForm/NewBiomarkerForm'
import { MoleculeSection } from './moleculeSection/MoleculeSection'
import { NameOfCGDSDataset } from '../../../../utils/interfaces'

/** ManualForm's props. */
interface ManualFormProps {
    biomarkerForm: FormBiomarkerData,
    /** Value for Checkbox. */
    checkedIgnoreProposedAlias: boolean,
    /** Handle change for Checkbox. */
    handleChangeIgnoreProposedAlias: (value: boolean) => void,
    removeSurvivalFormTuple: (datasetName: NameOfCGDSDataset, idxSurvivalTuple: number) => void,
    handleSurvivalFormDatasetChanges: (datasetName: NameOfCGDSDataset, idx: number, name: string, value: any) => void,
    cleanForm: () => void,
    isFormEmpty: () => boolean,
    handleChangeMoleculeSelected: (value: BiomarkerType) => void,
    handleChangeMoleculeInputSelected: (value: MoleculesTypeOfSelection) => void,
    handleAddMoleculeToSection: (value: MoleculesSectionData) => void,
    handleRemoveMolecule: (section: BiomarkerType, molecule: MoleculesSectionData) => void,
    handleGenesSymbolsFinder: (query: string) => void,
    handleGenesSymbols: (genes: string[]) => void,
    handleSelectOptionMolecule: (mol: MoleculesSectionData, section: BiomarkerType, itemSelected: string) => void,
    handleRemoveInvalidGenes: (sector: BiomarkerType) => void,
    handleChangeConfirmModalState: (setOption: boolean, headerText: string, contentText: string, onConfirm: Function) => void,
    handleValidateForm: () => { haveAmbiguous: boolean, haveInvalid: boolean },
    handleSendForm: () => void,
    handleChangeCheckBox: (value: boolean) => void,
    handleChangeInputForm: (value: string, name: 'biomarkerName' | 'biomarkerDescription') => void,

}

export const ManualForm = (props: ManualFormProps) => {
    return (
        <Grid columns={2} padded stackable divided className='biomarkers--modal--container'>
            <Grid.Column width={4} textAlign='left'>
                <NewBiomarkerForm
                    handleChangeInputForm={props.handleChangeInputForm}
                    biomarkerForm={props.biomarkerForm}
                    cleanForm={props.cleanForm}
                    isFormEmpty={props.isFormEmpty}
                    checkedIgnoreProposedAlias={props.checkedIgnoreProposedAlias}
                    handleChangeIgnoreProposedAlias={props.handleChangeIgnoreProposedAlias}
                    handleChangeMoleculeSelected={props.handleChangeMoleculeSelected}
                    handleChangeMoleculeInputSelected={props.handleChangeMoleculeInputSelected}
                    handleAddMoleculeToSection={props.handleAddMoleculeToSection}
                    handleGenesSymbolsFinder={props.handleGenesSymbolsFinder}
                    handleGenesSymbols={props.handleGenesSymbols}
                    handleChangeConfirmModalState={props.handleChangeConfirmModalState}
                    handleValidateForm={props.handleValidateForm}
                    handleSendForm={props.handleSendForm}
                    handleChangeCheckBox={props.handleChangeCheckBox}
                />
            </Grid.Column>
            <Asd
                biomarkerForm={props.biomarkerForm}
                handleRemoveMolecule={props.handleRemoveMolecule}
                handleSelectOptionMolecule={props.handleSelectOptionMolecule}
                handleRemoveInvalidGenes={props.handleRemoveInvalidGenes}
            />
        </Grid >
    )
}

interface Props {
    biomarkerForm: FormBiomarkerData,
    handleRemoveMolecule: (section: BiomarkerType, molecule: MoleculesSectionData) => void,
    handleSelectOptionMolecule: (mol: MoleculesSectionData, section: BiomarkerType, itemSelected: string) => void,
    handleRemoveInvalidGenes: (sector: BiomarkerType) => void,

}
// eslint-disable-next-line react/display-name
const Asd = React.memo(({
    biomarkerForm,
    handleRemoveMolecule,
    handleSelectOptionMolecule,
    handleRemoveInvalidGenes
}: Props) => {
    console.log('sssa')
    return (
        <Grid.Column width={12}>
            <Grid columns={2} stackable className='biomarkers--modal--container'>
                {Object.values(BiomarkerType).map(item => {
                    console.log('rend')
                    return (
                        <MoleculeSection
                            key={item}
                            title={item}
                            biomarkerFormData={biomarkerForm.moleculesSection[item]}
                            handleRemoveMolecule={handleRemoveMolecule}
                            handleSelectOptionMolecule={handleSelectOptionMolecule}
                            handleRemoveInvalidGenes={handleRemoveInvalidGenes}
                        />
                    )
                })}
            </Grid>
        </Grid.Column>
    )
})
