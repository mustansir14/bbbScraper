<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportBusinessInterface;
use DataExport\Exporters\ExportCompanyInterface;
use DataExport\Exporters\ExportComplaintInterface;
use DataExport\Exporters\ExportUserInterface;
use DataExport\Exporters\ExportCommentInterface;
use DataExport\Exporters\ExportCountryInterface;
use DataExport\Exporters\ExportStateInterface;

interface ExportInterface extends ExportBusinessInterface, ExportCompanyInterface, ExportComplaintInterface,
    ExportCommentInterface, ExportUserInterface, ExportCountryInterface
{
    public function getErrors(): array;
}