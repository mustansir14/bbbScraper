<?php
/**
 * @var bool $addComplaints
 * @var bool $removeComplaints
 * @var CBExport $exporter
 * @var array $sourceCompanyRow
 * @var Db $srcDb
 * @var Db $destDb
 */
if ( !$addComplaints ) {
    echo "Skip add complaints...\n";
    return;
}

use DataExport\Helpers\AddRecords;

$afterDate = $srcDb->selectColumn(
    'complaint_date',
    'complaint',
    "company_id = {$sourceCompanyRow["company_id"]}", false,"complaint_date desc", "14,1");
if ( $afterDate === false ) throw new Exception($srcDb->getError());
if ( !$afterDate ) {
    echo "Info: no complaint, may be review count < 14, skip\n";
    return;
}

echo "After data: {$afterDate}\n";

$complaints20 = $srcDb->queryArray("SELECT p.* FROM 
( 
    select * 
    from `complaint` 
    WHERE company_id='{$sourceCompanyRow["company_id"]}' and complaint_date < '{$afterDate}' 
    order by complaint_date desc 
) p 
order by char_length(complaint_text) DESC 
limit 16");

$skipIDs = [];
$insertedComplaints = [];

foreach( $complaints20 as $complaintNbr => $complaint )
{
    $skipIDs[] = $complaint["complaint_id"];

    $helper = new AddRecords([
        'counter' => $complaintNbr + 1,
        'isInsert' => true,
        'companyNameWithoutAbbr' => $companyNameWithoutAbbr,
        'exporter' => $exporter,
        'destCompanyID' => $destCompanyID,
        'destBusinessID' => $destBusinessID,
        'sourceCompanyRow' => $sourceCompanyRow,
        'importInfoScraper' => $importInfoScraper,
        'isDisableComplaints' => $isDisableComplaints,
        'ifResponseMakeResolved' => true,
        'checkTextInGoogle' => $checkTextInGoogle,
    ]);

    $complaintID = $helper->insertComplaint($complaint);
    if ( $complaintID ) {
        $insertedComplaints[] = $complaintID;
    }
}

$complaints16 = $srcDb->queryArray("select * 
from `complaint` 
WHERE company_id='{$sourceCompanyRow["company_id"]}' and complaint_date < '{$afterDate}' and complaint_id not in (".implode(",",$skipIDs).")
order by complaint_date desc 
limit 16");

# first complaint insert will be last in BN
$insertedComplaints = array_reverse($insertedComplaints);

$copyRowNumber = function ( array $insertedComplaints, array& $complaints16, int $index, int $max )
{
    $return = [];

    if ( isset( $insertedComplaints[$index] ) ) {
        $counter = 0;
        while ( $counter < $max && ( $row = array_shift( $complaints16) ) )
        {
            $return[] = [
                'to_complaint' =>  $insertedComplaints[$index],
                'row' => $row,
            ];
            $counter++;
        }
    }

    return $return;
};

$division = [];
$division = array_merge( $division, $copyRowNumber($insertedComplaints,$complaints16,0,4));
$division = array_merge( $division, $copyRowNumber($insertedComplaints,$complaints16,1,4));
$division = array_merge( $division, $copyRowNumber($insertedComplaints,$complaints16,2,4));
$division = array_merge( $division, $copyRowNumber($insertedComplaints,$complaints16,3,4));

foreach( $division as $complaintNbr => $divisionRow )
{
    $helper = new AddRecords([
        'counter' => $complaintNbr + 1,
        'isInsert' => true,
        'companyNameWithoutAbbr' => $companyNameWithoutAbbr,
        'exporter' => $exporter,
        'destCompanyID' => $destCompanyID,
        'destBusinessID' => $destBusinessID,
        'sourceCompanyRow' => $sourceCompanyRow,
        'importInfoScraper' => $importInfoScraper,
        'isDisableComplaints' => $isDisableComplaints,
        'checkTextInGoogle' => $checkTextInGoogle,
    ]);

    $helper->insertAsComment($divisionRow['row'], $divisionRow['to_complaint'], "complaint");
}
