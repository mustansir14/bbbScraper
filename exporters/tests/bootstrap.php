<?php
require __DIR__."/../vendor/autoload.php";

use DataExport\Helpers\Db;

global $db;

$db = new Db();
$db->connectOrDie( "localhost", "root", "", "cb" );