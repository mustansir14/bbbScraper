<?php

namespace DataExport\Data;

use DataExport\Formatters\PhoneFormatter;
use DataExport\Formatters\WebFormatter;
use DataExport\Formatters\HoursFormatter;
use DataExport\Helpers\BBBAPIHelper;
use DataExport\Helpers\ScreenshotApiHelper;
use DataExport\Data\CompanyData;
use DataExport\Data\FAQData;
use srgteam\klazify\KlazifyScraper;
use srgteam\klazify\TokenManager;
use SrgTeam\ScrapeWeb\Scraper as WebScraper;
use GuzzleHttp\Client;

class BusinessData
{
    private static function removeFAQ(object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr)
    {
        echo "Remove business FAQ: ".$sourceCompanyRow[ "company_id" ]."\n";
        $faqList = FAQData::prepare($sourceCompanyRow, $companyNameWithoutAbbr);
        if ($faqList) {
            FAQData::removeFAQFromBusiness($exporter, $sourceCompanyRow[ "company_id" ], $faqList);
        }
    }

    public static function removeAllPosts(object $exporter, array $sourceCompanyRow, string $type)
    {
        $businessID = $exporter->isBusinessExists(
            $exporter->getBusinessImportID($sourceCompanyRow[ 'company_id' ]),
            null
        );
        if ($businessID) {
            $types = [];
            if($type == "all") {
                $types[] = "review";
                $types[] = "complaint";
            }else{
                $types[] = $type;
            }

            foreach($types as $type) {
                foreach ($exporter->getAllImportedComments($businessID, $type) as $comment) {
                    #echo $comment[ 'import_id' ]."\n";
                    $exporter->removeCommentByImportID($comment['import_id']);
                }
                foreach ($exporter->getAllImportedComplaints($businessID, $type) as $complaint) {
                    #echo $complaint[ 'import_id' ]."\n";
                    $exporter->removeComplaintByImportID($complaint['import_id']);
                }
            }
        }
    }

    public static function unspamAllPosts(object $exporter, array $sourceCompanyRow, string $type)
    {
        $businessID = $exporter->isBusinessExists(
            $exporter->getBusinessImportID($sourceCompanyRow[ 'company_id' ]),
            null
        );
        if ($businessID) {
            foreach ($exporter->getAllImportedComments($businessID, $type) as $comment) {
                #echo $comment[ 'import_id' ]."\n";
                $exporter->unspamComment($comment[ 'import_id' ]);
            }
            foreach ($exporter->getAllImportedComplaints($businessID, $type) as $complaint) {
                #echo $complaint[ 'import_id' ]."\n";
                $exporter->unspamComplaint($complaint[ 'import_id' ]);
            }
        }
    }

    public static function remove(object $exporter, array $sourceCompanyRow, string $companyNameWithoutAbbr)
    {
        static::removeFAQ($exporter, $sourceCompanyRow, $companyNameWithoutAbbr);
        $businessID = $exporter->isBusinessExists(
            $exporter->getBusinessImportID($sourceCompanyRow[ 'company_id' ]),
            null
        );
        if ($businessID) {
            echo "Remove business & company: ".$sourceCompanyRow[ "company_id" ]."\n";
            static::removeAllPosts($exporter, $sourceCompanyRow, "review");
            static::removeAllPosts($exporter, $sourceCompanyRow, "complaint");
            if (!$exporter->removeCompanyByImportID($exporter->getCompanyImportID($sourceCompanyRow[ "company_id" ]))) {
                die($exporter->getErrorsAsString());
            }
            if (!$exporter->removeBusinessByImportID(
                $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ])
            )
            ) {
                die($exporter->getErrorsAsString());
            }
        }
    }

    private static function addSocialsToBNFromScrapeWeb(array $sourceCompanyRow, array &$bnameFields)
    {
        if ($sourceCompanyRow["website"] && filter_var(
                $sourceCompanyRow["website"],
                FILTER_VALIDATE_URL
            )
        ) {
            echo "Get socials from scrape web: {$sourceCompanyRow['website']}...\n";

            $scraper = new WebScraper();
            $socialMedia = $scraper->getSocials($sourceCompanyRow["website"]);
            if ($socialMedia === false) {
                $skipErrors = [
                    "Failed to connect to",
                    "CloudFlare challenge active",
                    "Http code is 403",
                ];

                $isSkip = false;
                foreach ($skipErrors as $findText) {
                    if (stripos($scraper->getError(), $findText) !== false) {
                        $isSkip = true;
                    }
                }

                if (!$isSkip) {
                    echo "ScrapeWeb::getSocials() error: ".$scraper->getError()."\n";
                }
            }

            $fields = [
                "facebook_url"  => "facebook",
                "twitter_url"   => "twitter",
                "instagram_url" => "instagram",
                "youtube_url"   => "youtube",
                "linkedin_url"  => "linkedin",
                "pinterest_url" => "pinterest",
            ];
            foreach ($fields as $scrapeWebFieldName => $cbFieldName) {
                if ($socialMedia[$scrapeWebFieldName] ?? false && count($socialMedia[$scrapeWebFieldName]) > 0) {
                    if (!isset($bnameFields[$cbFieldName]) || empty($bnameFields[$cbFieldName])) {
                        $bnameFields[$cbFieldName] = $socialMedia[$scrapeWebFieldName][0];

                        echo "ScrapeWeb {$cbFieldName}: {$bnameFields[$cbFieldName]}\n";
                    }
                }
            }
        }
    }

    private static function addSocialsToBNFromKlazify(array $sourceCompanyRow, array &$bnameFields)
    {
        if ($sourceCompanyRow["website"] && filter_var(
                $sourceCompanyRow["website"],
                FILTER_VALIDATE_URL
            )
        ) {
            echo "Get socials from klazify...\n";

            $scraper = new KlazifyScraper(TokenManager::get());
            #$scraper->verbose();

            $result = $scraper->getWebInformation($sourceCompanyRow["website"]);
            if ($result) {
                $socialMedia = $result['domain']['social_media'] ?? false;
                if ($socialMedia) {
                    # {
                    #   "facebook_url":"https:\/\/www.facebook.com\/CBSNews",
                    #   "twitter_url":"https:\/\/twitter.com\/CBSNews",
                    #   "instagram_url":"https:\/\/instagram.com\/cbsnews",
                    #   "medium_url":null,
                    #   "youtube_url":"http:\/\/www.youtube.com\/user\/CBSNewsOnline",
                    #   "pinterest_url":null,
                    #   "linkedin_url":null,
                    #   "github_url":null
                    #}

                    $fields = [
                        "facebook_url"  => "facebook",
                        "twitter_url"   => "twitter",
                        "instagram_url" => "instagram",
                        "youtube_url"   => "youtube",
                        "linkedin_url"  => "linkedin",
                        "pinterest_url" => "pinterest",
                    ];
                    foreach ($fields as $klazifyFieldName => $cbFieldName) {
                        if ($socialMedia[$klazifyFieldName] ?? false) {
                            if (!isset($bnameFields[$cbFieldName]) || empty($bnameFields[$cbFieldName])) {
                                $bnameFields[$cbFieldName] = $socialMedia[$klazifyFieldName];

                                echo "Klazify {$cbFieldName}: {$bnameFields[$cbFieldName]}\n";
                            }
                        }
                    }
                }
            }
        }
    }

    public static function createDbRecord(
        object $exporter,
        array $sourceCompanyRow,
        string $companyNameWithoutAbbr,
        string $importInfoScraper
    ) {
        $businessImportID = $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]);

        if (!preg_match('#bbb\.org/(us|ca)/#si', $sourceCompanyRow[ "url" ], $match)) {
            echo "Url: ".$sourceCompanyRow[ "url" ]."\n";
            die("Error:unknown country in url!");
        }

        $countryShortName = $match[ 1 ];
        $hours = $sourceCompanyRow[ "working_hours" ] ? HoursFormatter::fromString(
            $sourceCompanyRow[ "working_hours" ]
        ) : null;
        $hours = $hours ? HoursFormatter::convertToCBInternalFormat($hours) : null;

        $bnameFields = [
            "name"        => $companyNameWithoutAbbr,
            "ltd"         => $sourceCompanyRow[ "company_name" ],
            "country"     => $countryShortName,
            "state"       => $sourceCompanyRow[ "address_region" ],
            "city"        => $sourceCompanyRow[ "address_locality" ],
            "address"     => $sourceCompanyRow[ "street_address" ],
            "zip"         => $sourceCompanyRow[ "postal_code" ],
            "hours"       => $hours,
            "phone"       => PhoneFormatter::fromString($sourceCompanyRow[ "phone" ]),
            "fax"         => PhoneFormatter::fromString($sourceCompanyRow[ "fax_numbers" ]),
            "website"     => WebFormatter::fromString($sourceCompanyRow[ "website" ]),
            "category"    => "Other",
            "import_data" => [
                "company_id"   => $sourceCompanyRow[ "company_id" ],
                "company_name" => $sourceCompanyRow[ "company_name" ],
                "company_url"  => $sourceCompanyRow[ "url" ],
                "scraper"      => $importInfoScraper,
                "version"      => 1,
            ],
        ];

        static::addSocialsToBNFromScrapeWeb($sourceCompanyRow, $bnameFields);
        static::addSocialsToBNFromKlazify($sourceCompanyRow,$bnameFields);

        #print_r($bnameFields);

        $destBusinessID = $exporter->addBusiness($businessImportID, $bnameFields);

        if (!$destBusinessID) {
            die($exporter->getErrorsAsString());
        }

        echo "New business id: {$destBusinessID}\n";

        return $destBusinessID;
    }

    private static function uploadBBBLogo(array $sourceCompanyRow, object $exporter, string $businessImportID): bool
    {
        if ($sourceCompanyRow[ "logo" ]) {
            $bbbApi = new BBBAPIHelper();
            $image = $bbbApi->getLogo(basename($sourceCompanyRow[ "logo" ]));
            if ($image) {
                if (!$exporter->setBusinessLogo($businessImportID, $image)) {
                    die("setBusinessLogo Error: ".$exporter->getErrorsAsString());
                }

                return true;
            } else {
                echo "Logo error: ".$bbbApi->getError()."\n";
            }
        }

        return false;
    }

    private static function uploadKlazifyLogo(array $sourceCompanyRow, object $exporter, string $businessImportID): bool
    {
        if ($sourceCompanyRow[ "website" ] && filter_var(
                $sourceCompanyRow[ "website" ],
                FILTER_VALIDATE_URL
            )
        ) {
            echo "Get klazify information...\n";

            $scraper = new KlazifyScraper(TokenManager::get());
            $result = $scraper->getWebInformation($sourceCompanyRow[ "website" ]);
            if (!$result) {
                echo "Klazify error: ".$scraper->getError()."\n";
                return false;
            }

            $logo_url = $result[ 'domain' ][ 'logo_url' ] ?? false;
            if ($logo_url) {
                $client = new Client([
                    'verify'  => false,
                    'timeout' => 15,
                ]);

                echo "Download logo...\n";

                $response = $client->get($logo_url);
                if ($response->getStatusCode() != 200) {
                    die("Klazify logo code: ".$response->getStatusCode());
                }

                $contentType = $response->getHeader("Content-type")[ 0 ] ?? false;
                if (!preg_match("#^image/#si", $contentType)) {
                    die("Klazify logo content type: {$contentType}");
                }

                $body = $response->getBody()->getContents();
                if (!$exporter->setBusinessLogo($businessImportID, $body)) {
                    die("setBusinessLogo Error: ".$exporter->getErrorsAsString());
                }

                return true;
            } else {
                print_r($result);
                echo "Klazify no logo_url\n";
            }
        }

        return false;
    }

    private static function uploadWebScreenshotLogo(
        array $sourceCompanyRow,
        object $exporter,
        string $businessImportID,
        bool $makeScreenshot
    ): bool {
        if ($sourceCompanyRow[ "website" ] && filter_var(
                $sourceCompanyRow[ "website" ],
                FILTER_VALIDATE_URL
            ) && $makeScreenshot
        ) {
            echo "Making screenshot...\n";
            $screenshot = new ScreenshotApiHelper();
            $reply = $screenshot->getScreenshot($sourceCompanyRow[ "website" ]);
            if (!$reply) {
                var_dump($reply);
                echo "Error: making screenshot error: ".$screenshot->getError()."\n";
                return false;
            }
            if (!$exporter->setBusinessLogo($businessImportID, $reply->image_content)) {
                die("setBusinessLogo Error: ".$exporter->getErrorsAsString());
            }

            return true;
        }

        return false;
    }

    public static function uploadLogo(
        object $exporter,
        array $sourceCompanyRow,
        string $companyNameWithoutAbbr,
        bool $makeScreenshot
    ) {
        $businessImportID = $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]);
        // BN already can exists in db without exportation, do not modify this
        if ($exporter->isBusinessExported($businessImportID, $companyNameWithoutAbbr)) {
            echo "Logo: ".$sourceCompanyRow[ "logo" ]."\n";
            echo "Web: ".$sourceCompanyRow[ "website" ]."\n";

            if (static::uploadKlazifyLogo($sourceCompanyRow, $exporter, $businessImportID)) {
                return;
            }
            if (static::uploadWebScreenshotLogo($sourceCompanyRow, $exporter, $businessImportID, $makeScreenshot)) {
                return;
            }
            if (static::uploadBBBLogo($sourceCompanyRow, $exporter, $businessImportID)) {
                return;
            }
        }
    }

    public static function toggleProfile(object $exporter, array $sourceCompanyRow, bool $makeSpamComplaints)
    {
        $businessImportID = $exporter->getBusinessImportID($sourceCompanyRow[ "company_id" ]);
        $businessRow = $exporter->getBusiness($businessImportID);
        if ($businessRow) {
            if ($makeSpamComplaints) {
                $exporter->disableBusiness($businessImportID);
            } else {
                $exporter->enableBusiness($businessImportID);
            }
        }
    }

    private static function addFAQ(
        object $exporter,
        array $sourceCompanyRow,
        string $companyNameWithoutAbbr,
        string $importInfoScraper,
        int $destBusinessID
    ) {
        echo "Add business faq...\n";

        $faqList = FAQData::prepare($sourceCompanyRow, $companyNameWithoutAbbr);

        foreach ($faqList as $faqID => $faqRow) {
            $faqImportID = $exporter->getBusinessFAQImportID($destBusinessID, $faqRow[ "question" ]);
            $id = $exporter->addBusinessFAQ($faqImportID, [
                "business_id" => $destBusinessID,
                "question"    => $faqRow[ "question" ],
                "answer"      => $faqRow[ "answer" ],
                "import_data" => [
                    "company_id"       => $sourceCompanyRow[ "company_id" ],
                    "company_url"      => $sourceCompanyRow[ "url" ],
                    "business_started" => $sourceCompanyRow[ "business_started" ],
                    "scraper"          => $importInfoScraper,
                    "version"          => 1,
                ],
            ]);
            if (!$id) {
                die($exporter->getErrorsAsString());
            }
        }
    }

    public static function create(
        object $exporter,
        array $sourceCompanyRow,
        string $companyNameWithoutAbbr,
        string $importInfoScraper,
        bool $makeScreenshot,
        bool $makeSpamComplaints
    ) {
        $destCompanyID = CompanyData::create($exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper);
        if (!$destCompanyID) {
            throw new \Exception("critical");
        }
        $destBusinessID = $exporter->hasBusiness($destCompanyID);
        if (!$destBusinessID) {
            $destBusinessID = static::createDbRecord(
                $exporter,
                $sourceCompanyRow,
                $companyNameWithoutAbbr,
                $importInfoScraper
            );
            static::toggleProfile($exporter, $sourceCompanyRow, $makeSpamComplaints);
            static::uploadLogo($exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $makeScreenshot);
        } else {
            echo "Use BN id: {$destBusinessID}\n";
        }

        if (!$destBusinessID) {
            throw new \Exception("critical");
        }

        static::addFAQ($exporter, $sourceCompanyRow, $companyNameWithoutAbbr, $importInfoScraper, $destBusinessID);

        if (!$exporter->linkCompanyToBusiness($destCompanyID, $destBusinessID)) {
            die("linkCompanyToBusiness error: ".$exporter->getErrorsAsString());
        }

        return [
            $destBusinessID,
            $destCompanyID,
        ];
    }

}