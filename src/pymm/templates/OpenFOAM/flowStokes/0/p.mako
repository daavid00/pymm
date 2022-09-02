/*--------------------------------*- C++ -*----------------------------------*\
| =========                 |                                                 |
| \\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\    /   O peration     | Version:  v2206                                 |
|   \\  /    A nd           | Website:  www.openfoam.com                      |
|    \\/     M anipulation  |                                                 |
\*---------------------------------------------------------------------------*/
FoamFile
{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      [0 2 -2 0 0 0 0];

internalField   uniform 0;

boundaryField
{
    abovenbelow
    {
        type            empty;
    }
    inlet
    {
        type            fixedValue;
        value           uniform ${bc_inlet};   
    }
    outlet
    {
        type            fixedValue;
        value           uniform 0;   
    }
    defaultFaces
    {
        type            zeroGradient;
    }
}


// ************************************************************************* //
