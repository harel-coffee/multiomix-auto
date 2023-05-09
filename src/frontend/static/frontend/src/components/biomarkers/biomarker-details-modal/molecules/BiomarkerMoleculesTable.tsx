import React from 'react'
import { DropdownItemProps, Table } from 'semantic-ui-react'
import { Biomarker, BiomarkerMolecule } from '../../types'
import { PaginatedTable } from '../../../common/PaginatedTable'
import { TableCellWithTitle } from '../../../common/TableCellWithTitle'
import { MoleculeTypeLabel } from '../../labels/MoleculeTypeLabel'
import { MoleculeType } from '../../../../utils/interfaces'

declare const urlBiomarkerMolecules: string

/** BiomarkerMoleculesTable props. */
interface BiomarkerMoleculesTableProps {
    /** Selected Biomarker instance to retrieve all its molecules. */
    selectedBiomarker: Biomarker,
}

const moleculesTypesOptions: DropdownItemProps[] = [
    { key: MoleculeType.MRNA, text: 'mRNA', value: MoleculeType.MRNA },
    { key: MoleculeType.MIRNA, text: 'miRNA', value: MoleculeType.MIRNA },
    { key: MoleculeType.CNA, text: 'CNA', value: MoleculeType.CNA },
    { key: MoleculeType.METHYLATION, text: 'Methylation', value: MoleculeType.METHYLATION },
]

/**
 * Renders a Table with the samples and the cluster where they belong.
 * @param props Component props.
 * @returns Component.
 */
export const BiomarkerMoleculesTable = (props: BiomarkerMoleculesTableProps) => {
    return (
        <PaginatedTable<BiomarkerMolecule>
            headers={[
                { name: 'Identifier', serverCodeToSort: 'identifier', width: 3 },
                { name: 'Type', serverCodeToSort: 'type', width: 2 },
                { name: 'Actions' }
            ]}
            queryParams={{ biomarker_pk: props.selectedBiomarker.id }}
            customFilters={[
                { label: 'Type', keyForServer: 'type', defaultValue: '', options: moleculesTypesOptions }
            ]}
            defaultSortProp={{ sortField: 'identifier', sortOrderAscendant: true }}
            showSearchInput
            defaultPageSize={25}
            searchLabel='Sample'
            searchPlaceholder='Search by identifier'
            urlToRetrieveData={urlBiomarkerMolecules}
            mapFunction={(molecule: BiomarkerMolecule) => {
                return (
                    <Table.Row key={molecule.identifier}>
                        <TableCellWithTitle className='align-center' value={molecule.identifier} />
                        <Table.Cell><MoleculeTypeLabel moleculeType={molecule.type} /></Table.Cell>
                        <Table.Cell></Table.Cell>
                        {/* TODO: add action column to show its details */}
                        {/* TODO: add dblClick to show its details too */}
                        {/* <Table.Cell textAlign='center'>{molecule.cluster}</Table.Cell> */}
                    </Table.Row>
                )
            }}
        />
    )
}
