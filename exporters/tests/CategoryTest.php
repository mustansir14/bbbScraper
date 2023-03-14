<?php declare(strict_types=1);
use PHPUnit\Framework\TestCase;

use DataExport\Exporters\CBExport;
use DataExport\Helpers\Db;

final class CategoryTest extends TestCase
{
    private function getExport()
    {
        global $db;
        $cb = new CBExport($db, "");

        return $cb;
    }

    public function testParentCategory()
    {
        global $db;

        $db->delete('categories', ['name' => __FUNCTION__]) or die($db->getExtendedError());

        $export = $this->getExport();

        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__, null));

        $categoryID = $export->addCategory([
            "name" => __FUNCTION__,
            "import_data" => __FUNCTION__,
        ]);
        $this->assertIsInt($categoryID);
        $this->assertEquals($categoryID, $export->isCategoryExists(__FUNCTION__, null));

        $export->removeCategory(__FUNCTION__, null);

        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__, null));

        # check what will be on not existing category
        $export->removeCategory(__FUNCTION__, null);

        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__, null));
    }

    public function testChildCategory()
    {
        global $db;

        $db->delete('categories', ['name' => __FUNCTION__.'-child']) or die($db->getExtendedError());
        $db->delete('categories', ['name' => __FUNCTION__]) or die($db->getExtendedError());

        $export = $this->getExport();

        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__, null));
        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__.'-child', null));

        $categoryID = $export->addCategory([
            "name" => __FUNCTION__,
            "child_name" => __FUNCTION__.'-child',
            "import_data" => __FUNCTION__,
        ]);

        $this->assertIsInt($categoryID);

        $this->assertNotEquals($categoryID, $export->isCategoryExists(__FUNCTION__, null));
        $this->assertEquals($categoryID, $export->isCategoryExists(__FUNCTION__, __FUNCTION__.'-child'));

        $export->removeCategory(__FUNCTION__, __FUNCTION__.'-child');

        $this->assertNotEquals(0,$export->isCategoryExists(__FUNCTION__, null));
        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__.'-child', null));

        # check what will be on not existing category
        $export->removeCategory(__FUNCTION__, __FUNCTION__.'-child');

        $this->assertNotEquals(0,$export->isCategoryExists(__FUNCTION__, null));
        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__.'-child', null));

        $export->removeCategory(__FUNCTION__);

        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__, null));
        $this->assertEquals(0,$export->isCategoryExists(__FUNCTION__.'-child', null));
    }

    public function testLinkBusiness()
    {
        global $db;

        $export = $this->getExport();

        {
            $export->removeCategory(__FUNCTION__,__FUNCTION__.'-child');
            $export->removeCategory(__FUNCTION__,null);

            $categoryID = $export->addCategory([
                "name" => __FUNCTION__,
                "child_name" => __FUNCTION__.'-child',
                "import_data" => __FUNCTION__,
            ]);

            $this->assertIsInt($categoryID);
        }

        {
            $this->assertTrue(
                $export->removeBusinessByImportID($export->getBusinessImportID(__FUNCTION__)),
                "Can not remove Business"
            );

            $businessId = $export->addBusiness($export->getBusinessImportID(__FUNCTION__), [
                "name" => __FUNCTION__,
                "import_data" => __FUNCTION__,
            ]);

            $this->assertIsInt($businessId, "Result not int");
            $this->assertTrue($businessId > 0, "Business id zero");
        }

        $this->assertTrue($export->linkBusinessToAdditionalCategory($businessId, $categoryID));
        $this->assertEquals(1, $db->countRows('bname_categories',['bname_id' => $businessId, 'category_id' => $categoryID]));

        $this->assertTrue($export->linkBusinessToAdditionalCategory($businessId, $categoryID));
        $this->assertEquals(1, $db->countRows('bname_categories',['bname_id' => $businessId, 'category_id' => $categoryID]));
    }
}
