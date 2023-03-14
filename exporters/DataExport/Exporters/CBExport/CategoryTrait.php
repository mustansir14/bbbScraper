<?php
namespace DataExport\Exporters\CBExport;

use DataExport\Formatters\TextFormatter;

trait CategoryTrait
{
    public function isCategoryExists(string $parentCategory, ?string $childCategory = null)
    {
        $this->inputChecker->reset();

        $this->inputChecker->empty( $parentCategory, "Param: 'categoryName' is empty" );
        if ( $this->inputChecker->has() )
        {
            return false;
        }

        $categories = $childCategory ? [$parentCategory, $childCategory] : [$parentCategory];
        $parentID = null;
        $categoryID = 0;

        foreach($categories as $categoryName) {
            $categoryID = $this->db->selectColumn(
                "ID",
                "categories",
                ($parentID ? "parentID='{$parentID}'" : "parentID is null")." and lower(name)='".$this->db->escape(strtolower(trim($categoryName)))."'"
            );
            $this->throwExceptionIf($categoryID === false, $this->db->getExtendedError());

            $parentID = $categoryID;
        }

        return $categoryID ? (int)$categoryID: 0;
    }

    public function getCategoryImportID(string $parentCategory, ?string $childCategory = null): string
    {
        return "bbb-mustansir-scraper:/{$parentCategory}".($childCategory ? "/".$childCategory : "");
    }

    public function removeCategory(string $parentCategory, ?string $childCategory = null)
    {
        $this->inputChecker->reset();

        if($childCategory) {
            # remove only child category, because on parent may be many categories
            return $this->removeRecordByImportID("categories", $this->getCategoryImportID($parentCategory, $childCategory));
        }

        return $this->removeRecordByImportID( "categories", $this->getCategoryImportID($parentCategory) );
    }

    public function linkBusinessToAdditionalCategory(int $businessID, int $categoryID)
    {
        if($this->db->countRows('bname_categories', ['bname_id' => $businessID, 'category_id' => $categoryID]) == 0)
        {
            $rs = $this->db->insert( "bname_categories", [
                'bname_id' => $businessID,
                'category_id' => $categoryID
            ]);

            $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );
        }

        return true;
    }

    public function addCategory(array $fields)
    {
        $this->inputChecker->reset();

        $checker = $this->inputChecker;

        $checker->empty( $fields, "Param: fields is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $parentRip = TextFormatter::rip( $fields["name"] ?? "" );
        $childRip  = TextFormatter::rip( $fields["child_name"] ?? "" );

        if ( !$checker->empty( $fields['name'], "Field: 'name' is empty" ) )
        {
            if ( !$parentRip )
            {
                $checker->append( "Rip for name invalid" );
            }
        }

        if( isset( $fields['child_name'] ) )
        {
            if(!$checker->empty( $fields['child_name'], "Field: 'child_name' is empty" ))
            {
                if ( !$childRip )
                {
                    $checker->append( "Rip for child_name invalid" );
                }
            }
        }

        $checker->empty( $fields["import_data"], "Field: 'import_data' is empty" );

        if ( $checker->has() )
        {
            return false;
        }

        $parentID = $this->isCategoryExists( $fields["name"] );
        if ( $parentID == 0 ) {
            $insertFields = [
                "parentID" => null,
                "name"     => $fields["name"],
                "link"     => $parentRip,
            ];

            $rs = $this->db->insert( "categories", $insertFields );
            $this->throwExceptionIf( !$rs, $this->db->getExtendedError() );

            $parentID = $this->db->insertID();
            $this->throwExceptionIf( $parentID < 1, "No id" );

            $this->addImport( "categories", $parentID, $this->getCategoryImportID($fields['name']), $fields["import_data"] );
        }

        if( isset( $fields['child_name'] ) )
        {
            $childID = $this->isCategoryExists( $fields["name"],$fields["child_name"] );
            if($childID == 0) {
                $insertFields = [
                    "parentID" => $parentID,
                    "name"     => $fields["child_name"],
                    "link"     => $childRip,
                ];

                $rs = $this->db->insert("categories", $insertFields);
                $this->throwExceptionIf(!$rs, $this->db->getExtendedError());

                $childID = $this->db->insertID();
                $this->throwExceptionIf($childID < 1, "No id");

                $this->addImport(
                    "categories",
                    $childID,
                    $this->getCategoryImportID($fields['name'], $fields['child_name']),
                    $fields["import_data"]
                );
            }

            return $childID;
        }

        return $parentID;
    }
}