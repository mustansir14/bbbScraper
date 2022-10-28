<?php
namespace DataExport\Exporters\CBExport;

trait CategoryTrait
{
    public function isCategoryExists( string $categoryName )
    {
        $this->inputChecker->reset();

        $this->inputChecker->empty( $categoryName, "Param: 'categoryName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        $categoryID = $this->db->selectColumn(
            "ID",
            "categories",
            "lower(name)='". $this->db->escape( strtolower( trim( $categoryName ) ) )."'"
        );
        $this->throwExceptionIf( $categoryID === false, $this->db->getExtendedError() );

        return $categoryID ? (int)$categoryID: 0;
    }
}