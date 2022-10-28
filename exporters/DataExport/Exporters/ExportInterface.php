<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportBusinessInterface;
use DataExport\Exporters\ExportCompanyInterface;
use DataExport\Exporters\ExportComplaintInterface;
use DataExport\Exporters\ExportUserInterface;
use DataExport\Exporters\ExportCommentInterface;
use DataExport\Exporters\ExportCountryInterface;
use DataExport\Exporters\ExportStateInterface;
use DataExport\Exporters\ExportBusinessFAQInterface;

interface ExportInterface extends ExportBusinessInterface, ExportCompanyInterface, ExportComplaintInterface,
    ExportCommentInterface, ExportUserInterface, ExportCountryInterface, ExportCategoryInterface, ExportBusinessFAQInterface
{
    public function getErrors(): array;
}