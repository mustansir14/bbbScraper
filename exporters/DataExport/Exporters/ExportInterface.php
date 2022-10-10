<?php
namespace DataExport\Exporters;

use DataExport\Exporters\ExportBusinessInterface;
use DataExport\Exporters\ExportCompanyInterface;
use DataExport\Exporters\ExportComplaintInterface;
use DataExport\Exporters\ExportUserInterface;
use DataExport\Exporters\ExportCommentInterface;

interface ExportInterface extends ExportBusinessInterface, ExportCompanyInterface, ExportComplaintInterface, ExportCommentInterface, ExportUserInterface
{
    public function getErrors(): array;
}