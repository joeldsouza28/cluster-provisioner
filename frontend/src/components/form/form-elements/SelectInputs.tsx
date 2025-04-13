import { useState } from "react";
import ComponentCard from "../../common/ComponentCard";
import Label from "../Label";
import Select from "../Select";
import MultiSelect from "../MultiSelect";

export default function SelectInputs({options, label, handleSelectChange}) {
  // const options = [
    // { value: "marketing", label: "Marketing" },
    // { value: "template", label: "Template" },
    // { value: "development", label: "Development" },
  // ];
  // const handleSelectChange = (value: string) => {
  //   console.log("Selected value:", value);
  // };

  
  return (
      <div className="space-y-6">
        <div>
          <Label>{label}</Label>
          <Select
            options={options}
            placeholder="Select Option"
            onChange={handleSelectChange}
            className="dark:bg-dark-900"
          />
        </div>
      </div>
  );
}
