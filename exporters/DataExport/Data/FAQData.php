<?php
namespace DataExport\Data;

class FAQData
{
    public static function prepare( array $sourceCompanyRow, string $companyNameWithoutAbbr ): array
    {
        $faqList = [];

        if( $sourceCompanyRow["business_started"] )
        {
            $date = strtotime( $sourceCompanyRow["business_started"] );
            if ( $date > mktime( 1, 1, 1, 1, 1, 1500 ) )
            {
                $date = date( "m-d-Y", $date );
                $question = "When {$companyNameWithoutAbbr} was founded?";
                $answer =  "{$companyNameWithoutAbbr} was founded on {$date}.";

                $faqList[] = [
                    "question" => $question,
                    "answer"   => $answer,
                ];
            }
        }

        if ( $sourceCompanyRow["type_of_entity"] )
        {
            $answer = "{$companyNameWithoutAbbr} is a {$sourceCompanyRow['type_of_entity']}. ";
            $helpers = [
                "Corporation" => "A corporation is a legal entity created by individuals, stockholders, or shareholders, with the purpose of operating for profit. Corporations are allowed to enter into contracts, sue and be sued, own assets, remit federal and state taxes, and borrow money from financial institutions.",
                "Limited Liability Company (LLC)" => "A limited liability company is the US-specific form of a private limited company. It is a business structure that can combine the pass-through taxation of a partnership or sole proprietorship with the limited liability of a corporation.",
                "Cooperative Association" => "A co-operative or co-op is a business that is owned and controlled by its members in order to provide goods or services to those members. Each member pays a membership fee or purchases a membership share and has one vote regardless of the amount of money they have invested in the co-op.",
                "General Partnership" => "A general partnership is a business established by two or more owners. It is the default business structure for multiple owners the same way that a sole proprietorship is the default for solo entrepreneurs.",
                "Limited Liability Partnership (LLP)" => "What is a Limited Liability Partnership (LLP)?\nA limited liability partnership is a partnership in which some or all partners have limited liabilities. It therefore can exhibit elements of partnerships and corporations. In an LLP, each partner is not responsible or liable for another partner's misconduct or negligence.",
                "Limited Partnership" => "A limited partnership is a form of partnership similar to a general partnership except that while a general partnership must have at least two general partners, a limited partnership must have at least one GP and at least one limited partner.",
                "Non-Profit Organization" => "A non-profit organization is a legal entity organized and operated for a collective, public or social benefit, in contrast with an entity that operates as a business aiming to generate a profit for its owners.",
                "Partnership" => "What is a Partnership?\nA partnership is an arrangement where parties, known as business partners, agree to cooperate to advance their mutual interests. The partners in a partnership may be individuals, businesses, interest-based organizations, schools, governments or combinations.",
                "Private Limited Company (LTD)" => "A private limited company is any type of business entity in \"private\" ownership used in many jurisdictions, in contrast to a publicly listed company, with some differences from country to country.",
                "Private Company Limited by Shares" => "What is a Private Company Limited by Shares?\nA private company limited by shares is a class of private limited company incorporated under the laws of England and Wales, Northern Ireland, Scotland, certain Commonwealth countries, and the Republic of Ireland. 
",
                "Professional Corporation" => "Professional corporations or professional service corporation are those corporate entities for which many corporation statutes make special provision, regulating the use of the corporate form by licensed professionals such as attorneys, architects, engineers, public accountants and physicians.",
                "S Corporation" => "An S corp or S corporation is a business structure that is permitted under the tax code to pass its taxable income, credits, deductions, and losses directly to its shareholders. That gives it certain advantages over the more common C corp, The S corp is available only to small businesses with 100 or fewer shareholders, and is an alternative to the limited liability company (LLC).",
                "Sole Proprietorship" => "A sole proprietorship, also known as a sole tradership, individual entrepreneurship or proprietorship, is a type of enterprise owned and run by one person and in which there is no legal distinction between the owner and the business entity. A sole trader does not necessarily work alone and may employ other people.",
            ];

            $advance = "";

            foreach( $helpers as $title => $text )
            {
                if ( strcasecmp( $title, $sourceCompanyRow["type_of_entity"] ) == 0 )
                {
                    $advance = $text;
                    break;
                }
            }

            if ( !$advance ) die( "Unknown type: ".$sourceCompanyRow["type_of_entity"] );

            $answer .= $advance;

            $faqList[] = [
                "question" => "What type of business entity is {$companyNameWithoutAbbr}?",
                "answer"   => nl2br( $answer ),
            ];
        }

        if ( $sourceCompanyRow['number_of_employees'] )
        {
            $faqList[] = [
                "question" => "How many employees does {$companyNameWithoutAbbr} have?",
                "answer"   => "As per our latest record, {$companyNameWithoutAbbr} has {$sourceCompanyRow['number_of_employees']} employees.",
            ];
        }

        $management = $sourceCompanyRow['business_management'] ?? "";
        $management = trim( $management, " \t\r\n,.-*" );

        if ( $management && 0)
        {
            $faqList[] = [
                "question" => "Who's in charge of {$companyNameWithoutAbbr} business management?",
                "answer"   => "As per our latest record, {$companyNameWithoutAbbr} has {$sourceCompanyRow['number_of_employees']} employees",
            ];
        }

        $area = $sourceCompanyRow['serving_area'] ?? "";
        $area = trim( $area );
        if ( $area )
        {
            $faqList[] = [
                "question" => "What is current serving area of {$companyNameWithoutAbbr}?",
                "answer"   => rtrim( $area, " \t\r\n." ).".",
            ];
        }

        $productAndServices = $sourceCompanyRow["products_and_services"] ?? "";
        $productAndServices = trim( $productAndServices );

        if( $productAndServices )
        {
            $faqList[] = [
                "question" => "What products & services does {$companyNameWithoutAbbr} offer?",
                "answer"   => rtrim( $productAndServices, " \t\r\n." ).".",
            ];
        }

        return $faqList;
    }

    public static function removeFAQFromBusiness( object $exporter, int $companyID, array $faqList )
    {
        $businessID = $exporter->isBusinessExists( $exporter->getBusinessImportID( $companyID ), null );

        if ( $businessID )
        {
            foreach( $faqList as $faqID => $faqRow )
            {
                if ( !$exporter->removeBusinessFAQByImportID( $exporter->getBusinessFAQImportID( $businessID, $faqRow["question"] ) ) )
                {
                    die( $exporter->getErrorsAsString() );
                }
            }
        }
    }
}