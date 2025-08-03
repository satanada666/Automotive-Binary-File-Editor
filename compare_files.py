def compare_binary_files(file1_path, file2_path, output_file):
    with open(file1_path, 'rb') as f1, open(file2_path, 'rb') as f2:
        data1 = f1.read()
        data2 = f2.read()
        
        if len(data1) != len(data2):
            print("Файлы имеют разную длину! Сравнение возможно только до минимальной длины.")
            min_len = min(len(data1), len(data2))
            data1 = data1[:min_len]
            data2 = data2[:min_len]
        else:
            min_len = len(data1)
        
        with open(output_file, 'w') as out:
            # Заголовок отчета
            out.write("Address    File1_Byte    File2_Byte\n")
            # Сравнение побайтно
            for i in range(min_len):
                if data1[i] != data2[i]:
                    out.write(f"0x{i:06X}   0x{data1[i]:02X}        0x{data2[i]:02X}\n")
            print(f"Отчет сохранен в {output_file}")

# Пример использования
compare_binary_files(
    "CG100X_1_8_8_2_20250706_001801_BMW_SME_Battery_Management_Module(crash).bin",
    "CG100X_1_8_9_0_20250723_135144_BMW_SME_Battery_Management_Module(clear).bin",
    "differences.txt"
)