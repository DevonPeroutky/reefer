from app.actions.find_company_action import FindCompanyAction


class StubService:

    async def find_company_information(self, company_name: str):

        # 1. Find company
        find_company_action = FindCompanyAction(
            serp_service=self.serp_service,
            scraping_service=self.scraping_service,
        )

        async for event in find_company_action.yield_action_stream(company_name):
            print("Yielding event: ", event)
            yield event

        self.company = find_company_action.yield_action_result()
        print(f"TODO: Asynchronously write ({self.company} to DB")

        # 2. Parse openings
        parse_openings_action = ParseOpeningsAction()
        async for event in parse_openings_action.yield_action_stream(
            company=self.company, job_type="Software Engineer"
        ):
            print("Yielding parse openings: ", event)
            yield event

        self.openings = parse_openings_action.yield_action_result()
        print(self.openings)
        print(f"TODO: Asynchronously write {self.openings} to DB")
