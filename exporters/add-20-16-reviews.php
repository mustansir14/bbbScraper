<?php
/**
 * @var bool $addComplaints
 * @var bool $removeComplaints
 * @var bool $checkTextInGoogle
 * @var CBExport $exporter
 * @var array $sourceCompanyRow
 * @var Db $srcDb
 * @var Db $destDb
 * @var object $checkUniqueViaCSV
 */
if ( !$addComplaints ) return;

use DataExport\Helpers\AddRecords;

echo "Select review_date...\n";

$afterDate = $srcDb->selectColumn(
    'review_date',
    'review',
    "company_id = {$sourceCompanyRow["company_id"]}", false,"review_date desc", "14,1");
if ( $afterDate === false ) throw new \Exception( __LINE__ );
if ( !$afterDate ) {
    echo "Info: no reviews, may be review count < 14, skip\n";
    return;
}

echo "After data: {$afterDate}\n";

$complaints20 = $srcDb->queryArray("SELECT p.* FROM 
( 
    select * 
    from `review` 
    WHERE company_id='{$sourceCompanyRow["company_id"]}' and review_date < '{$afterDate}' 
    order by review_date desc 
) p 
order by char_length(review_text) DESC 
limit 25");
if ( $complaints20 === false ) throw new \Exception( __LINE__ );

$skipIDs = [];
$insertedComplaints = [];

foreach( $complaints20 as $complaintNbr => $complaint )
{
    $skipIDs[] = $complaint["review_id"];

    $helper = new AddRecords([
        'counter' => $complaintNbr + 1,
        'isInsert' => true,
        'companyNameWithoutAbbr' => $companyNameWithoutAbbr,
        'exporter' => $exporter,
        'destCompanyID' => $destCompanyID,
        'destBusinessID' => $destBusinessID,
        'sourceCompanyRow' => $sourceCompanyRow,
        'importInfoScraper' => $importInfoScraper,
        'makeSpamComplaints' => $makeSpamComplaints,
        'checkTextInGoogle' => $checkTextInGoogle,
    ]);

    if($checkUniqueViaCSV->isModeCollect()) {
        $checkUniqueViaCSV->saveRecord($complaint['review_id'], $complaint['review_text']);
    } elseif($checkUniqueViaCSV->isModeUse()) {
        if(!$checkUniqueViaCSV->isIDUnique($complaint['review_id'])) {
            echo "Text not unique for {$complaint['review_id']}, skip...\n";
            continue;
        }
    }

    $complaintID = $helper->insertReview($complaint);
    if ( $complaintID ) {
        $insertedComplaints[] = $complaintID;
    }
}

$complaints16 = $srcDb->queryArray("select * 
from `review` 
WHERE company_id='{$sourceCompanyRow["company_id"]}' and review_date < '{$afterDate}' and review_id not in (".implode(",",$skipIDs).")
order by review_date desc 
limit 16");
if ( $complaints16 === false ) throw new \Exception( $srcDb->getExtendedError() );

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
        'makeSpamComplaints' => $makeSpamComplaints,
        'checkTextInGoogle' => $checkTextInGoogle,
    ]);

    if($checkUniqueViaCSV->isModeCollect()) {
        $checkUniqueViaCSV->saveRecord($divisionRow['row']['review_id'], $divisionRow['row']['review_text']);
    } elseif($checkUniqueViaCSV->isModeUse()) {
        if(!$checkUniqueViaCSV->isIDUnique($divisionRow['row']['review_id'])) {
            echo "Text not unique for {$divisionRow['row']['review_id']}, skip...\n";
            continue;
        }
    }

    $helper->insertAsComment($divisionRow['row'], $divisionRow['to_complaint'], $complaintType);
}
